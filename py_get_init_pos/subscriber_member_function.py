# Filenames for param input and output
input_file = "/home/orin/Desktop/launch_files/nav2_gps/scout/params/scout_dual_ekf_navsat_params.backup.yaml"
# Note that the output file WILL BE OVERWRITTEN when the node runs
output_file = "/home/orin/Desktop/launch_files/nav2_gps/scout/params/scout_dual_ekf_navsat_params.yaml"

'''
Python version of the inline functions defined in the robot_localization, 
navsat_conversions.h
'''

from math import *
import re

RADIANS_PER_DEGREE = pi/180.0;
DEGREES_PER_RADIAN = 180.0/pi;

# Grid granularity for rounding UTM coordinates to generate MapXY.
grid_size = 100000.0;    # 100 km grid

# WGS84 Parameters
WGS84_A =6378137.0   # major axis
WGS84_B =6356752.31424518  # minor axis
WGS84_F =0.0033528107    # ellipsoid flattening
WGS84_E =0.0818191908    # first eccentricity
WGS84_EP =0.0820944379    # second eccentricity

# UTM Parameters
UTM_K0  =  0.9996               # scale factor
UTM_FE  = 500000.0             # false easting
UTM_FN_N = 0.0                  # false northing, northern hemisphere
UTM_FN_S = 10000000.0           # false northing, southern hemisphere
UTM_E2   = (WGS84_E*WGS84_E)    # e^2
UTM_E4   = (UTM_E2*UTM_E2)      # e^4
UTM_E6   = (UTM_E4*UTM_E2)      # e^6
UTM_EP2  = (UTM_E2/(1-UTM_E2))  # e'^2


def ll2xy(lat,lon,origin_lat,origin_lon):
    '''
    Geonav: Lat/Long to X/Y
    Convert latitude and longitude in dec. degress to x and y in meters
    relative to the given origin location.  Converts lat/lon and orgin to UTM and then takes the difference

    Args:
      lat (float): Latitude of location
      lon (float): Longitude of location
      orglat (float): Latitude of origin location
      orglon (float): Longitude of origin location

    Returns:
      tuple: (x,y) where...
        x is Easting in m (local grid)
        y is Northing in m  (local grid)
    '''

    outmy, outmx, outmzone = LLtoUTM(origin_lat,origin_lon)
    utmy, utmx, utmzone = LLtoUTM(lat,lon)
    if (not (outmzone==utmzone)):
        print('WARNING: geonav_conversion: origin and location are in different UTM zones!')
    y = utmy-outmy
    x = utmx-outmx
    return (x,y) 

def xy2ll(x, y, orglat, orglon):
    '''
    '''
    outmy, outmx, outmzone = LLtoUTM(orglat,orglon)
    utmy = outmy+y
    utmx = outmx+x
    return UTMtoLL(utmy,utmx,outmzone)

'''*
 * Determine the correct UTM letter designator for the
 * given latitude
 *
 * @returns 'Z' if latitude is outside the UTM limits of 84N to 80S
 *
 * Written by Chuck Gantz- chuck.gantz@globalstar.com
 '''
def UTMLetterDesignator(Lat):
    
    LetterDesignator =""

    if ((84 >= Lat) and (Lat >= 72)):  LetterDesignator = 'X'
    
    elif ((72 > Lat) and (Lat >= 64)):  LetterDesignator = 'W';
    elif ((64 > Lat) and (Lat >= 56)):  LetterDesignator = 'V';
    elif ((56 > Lat) and (Lat >= 48)):  LetterDesignator = 'U';
    elif ((48 > Lat) and (Lat >= 40)):  LetterDesignator = 'T';
    elif ((40 > Lat) and (Lat >= 32)):  LetterDesignator = 'S';
    elif ((32 > Lat) and (Lat >= 24)):  LetterDesignator = 'R';
    elif ((24 > Lat) and (Lat >= 16)):  LetterDesignator = 'Q';
    elif ((16 > Lat) and (Lat >= 8)) :  LetterDesignator = 'P';
    elif (( 8 > Lat) and (Lat >= 0)) :  LetterDesignator = 'N';
    elif (( 0 > Lat) and (Lat >= -8)):  LetterDesignator = 'M';
    elif ((-8 > Lat) and (Lat >= -16)): LetterDesignator = 'L';
    elif ((-16 > Lat) and (Lat >= -24)): LetterDesignator = 'K';
    elif ((-24 > Lat) and (Lat >= -32)): LetterDesignator = 'J';
    elif ((-32 > Lat) and (Lat >= -40)): LetterDesignator = 'H';
    elif ((-40 > Lat) and (Lat >= -48)): LetterDesignator = 'G';
    elif ((-48 > Lat) and (Lat >= -56)): LetterDesignator = 'F';
    elif ((-56 > Lat) and (Lat >= -64)): LetterDesignator = 'E';
    elif ((-64 > Lat) and (Lat >= -72)): LetterDesignator = 'D';
    elif ((-72 > Lat) and (Lat >= -80)): LetterDesignator = 'C';
        # 'Z' is an error flag, the Latitude is outside the UTM limits
    else: LetterDesignator = 'Z';
    return LetterDesignator


'''*
 * Convert lat/long to UTM coords.  Equations from USGS Bulletin 1532
 *
 * East Longitudes are positive, West longitudes are negative.
 * North latitudes are positive, South latitudes are negative
 * Lat and Long are in fractional degrees
 *
 * Written by Chuck Gantz- chuck.gantz@globalstar.com
 Retuns a tuple of (UTMNorthing, UTMEasting, UTMZone)
 '''
def LLtoUTM(Lat,Long):

  a = WGS84_A;
  eccSquared = UTM_E2;
  k0 = UTM_K0;

  # Make sure the longitude is between -180.00 .. 179.9
  LongTemp = (Long+180.0)-int((Long+180.)/360.)*360.-180.;

  LatRad = Lat*RADIANS_PER_DEGREE;
  LongRad = LongTemp*RADIANS_PER_DEGREE;
  ZoneNumber = int((LongTemp + 180.0)/6.0) + 1;

  if ( Lat >= 56.0 and Lat < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0 ):
      ZoneNumber = 32;
        # Special zones for Svalbard
  if ( Lat >= 72.0 and Lat < 84.0 ):
      if (      LongTemp >= 0.0  and LongTemp <  9.0 ): ZoneNumber = 31;
      elif ( LongTemp >= 9.0  and LongTemp < 21.0 ): ZoneNumber = 33;
      elif ( LongTemp >= 21.0 and LongTemp < 33.0 ): ZoneNumber = 35;
      elif ( LongTemp >= 33.0 and LongTemp < 42.0 ): ZoneNumber = 37;
  # +3 puts origin in middle of zone
  LongOrigin = (ZoneNumber - 1.0)*6.0 - 180.0 + 3.0;
  LongOriginRad = LongOrigin * RADIANS_PER_DEGREE;

  # Compute the UTM Zone from the latitude and longitude
  UTMZone = "%d%s"%(ZoneNumber,UTMLetterDesignator(Lat))
  #print("UTM Zone: %s"%(UTMZone))
  eccPrimeSquared = (eccSquared)/(1.0-eccSquared);
  N = a/sqrt(1-eccSquared*sin(LatRad)*sin(LatRad));
  T = tan(LatRad)*tan(LatRad);
  C = eccPrimeSquared*cos(LatRad)*cos(LatRad);
  A = cos(LatRad)*(LongRad-LongOriginRad);
  
  M = a*((1 - eccSquared/4.0 - 3.0*eccSquared*eccSquared/64.0
          - 5.0*eccSquared*eccSquared*eccSquared/256.0) * LatRad
         - (3.0*eccSquared/8.0 + 3.0*eccSquared*eccSquared/32.0
            + 45.0*eccSquared*eccSquared*eccSquared/1024.0)*sin(2.0*LatRad)
         + (15.0*eccSquared*eccSquared/256.0
            + 45.0*eccSquared*eccSquared*eccSquared/1024.0)*sin(4.0*LatRad)
         - (35.0*eccSquared*eccSquared*eccSquared/3072.0)*sin(6.0*LatRad));

  UTMEasting = (k0*N*(A+(1.0-T+C)*A*A*A/6.0
                      + (5.0-18.0*T+T*T+72*C
                         - 58.0*eccPrimeSquared)*A*A*A*A*A/120.0)
                + 500000.0)

  UTMNorthing = (k0*(M+N*tan(LatRad)
                     *(A*A/2.0+(5.0-T+9.0*C+4.0*C*C)*A*A*A*A/24.0
                       + (61.0-58.0*T+T*T+600.0*C
                          - 330.0*eccPrimeSquared)*A*A*A*A*A*A/720.0)));
  if (Lat < 0):
      # 10000000 meter offset for southern hemisphere
      UTMNorthing += 10000000.0;
  
  return (UTMNorthing, UTMEasting, UTMZone)

'''*
 * Converts UTM coords to lat/long.  Equations from USGS Bulletin 1532
 *
 * East Longitudes are positive, West longitudes are negative.
 * North latitudes are positive, South latitudes are negative
 * Lat and Long are in fractional degrees.
 *
 * Written by Chuck Gantz- chuck.gantz@globalstar.com
 Returns (Lat, Lon, UTMZone)
 '''
def UTMtoLL(UTMNorthing,UTMEasting,UTMZone):
  k0 = UTM_K0;
  a = WGS84_A;
  eccSquared = UTM_E2;
  e1 = (1-sqrt(1-eccSquared))/(1+sqrt(1-eccSquared));

  x = UTMEasting - 500000.0;  # remove 500,000 meter offset for longitude
  y = UTMNorthing;
  
  ZoneLetter = re.findall('([a-zA-Z])',UTMZone)[0]
  ZoneNumber = float( UTMZone.split(ZoneLetter)[0] )

  if (ZoneLetter <'N'):
      # remove 10,000,000 meter offset used for southern hemisphere
      y -= 10000000.0;

  # +3 puts origin in middle of zone
  LongOrigin = (ZoneNumber - 1)*6.0 - 180.0 + 3.0;
  eccPrimeSquared = (eccSquared)/(1.0-eccSquared);
  M = y / k0;
  mu = M/(a*(1.0-eccSquared/4.0-3.0*eccSquared*eccSquared/64.0
             -5.0*eccSquared*eccSquared*eccSquared/256.0));
  phi1Rad = mu + ((3.0*e1/2.0-27.0*e1*e1*e1/32.0)*sin(2.0*mu)
                  + (21.0*e1*e1/16.0-55.0*e1*e1*e1*e1/32.0)*sin(4.0*mu)
                  + (151.0*e1*e1*e1/96.0)*sin(6.0*mu));
  
  N1 = a/sqrt(1.0-eccSquared*sin(phi1Rad)*sin(phi1Rad));
  T1 = tan(phi1Rad)*tan(phi1Rad);
  C1 = eccPrimeSquared*cos(phi1Rad)*cos(phi1Rad);
  R1 = a*(1.0-eccSquared)/pow(1-eccSquared*sin(phi1Rad)*sin(phi1Rad), 1.5);
  D = x/(N1*k0);
  Lat = phi1Rad - ((N1*tan(phi1Rad)/R1)
                   *(D*D/2.0
                     -(5.0+3.0*T1+10.0*C1-4.0*C1*C1
                       -9.0*eccPrimeSquared)*D*D*D*D/24.0
                     +(61.0+90.0*T1+298.0*C1+45.0*T1*T1-252.0*eccPrimeSquared
                       -3.0*C1*C1)*D*D*D*D*D*D/720.0));
  
  Lat = Lat * DEGREES_PER_RADIAN;
  
  Long = ((D-(1.0+2.0*T1+C1)*D*D*D/6.0
           +(5.0-2.0*C1+28.0*T1-3.0*C1*C1+8.0*eccPrimeSquared+24.0*T1*T1)
           *D*D*D*D*D/120.0)
          / cos(phi1Rad));
  Long = LongOrigin + Long * DEGREES_PER_RADIAN;

  return (Lat, Long)

# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            NavSatFix,
            'nav_sat_fix',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('Recieved Data')
        d,e,f = LLtoUTM(44.663,-75.00)
        a,b,c = LLtoUTM(msg.latitude,msg.longitude)
        g = a-d
        h = b-e
        print(c)
        fi = open(input_file, 'r')
        fd = open(output_file, 'w')
        i = fi.readline()
        while (i != ""):
            j = i.find("initial_state:")
            if j == -1:
                fd.write(i)
            else:
                fd.write("    initial_state: [")
                fd.write(repr(h))
                fd.write(", ")
                fd.write(repr(g))
                fd.write(", 0.0,\n")
            i = fi.readline()
        #self.get_logger().info('I heard: "%s"' % msg.data)
        self.destroy_node()

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
