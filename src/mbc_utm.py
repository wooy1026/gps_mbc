#!/usr/bin/env python3
import rospy
import utm
from nmea_msgs.msg import Sentence
from std_msgs.msg import Float64

def listener():
    rospy.init_node('gps_listener', anonymous=True)

    pub_heading = rospy.Publisher('heading_topic', Float64, queue_size=30)
    pub_latitude = rospy.Publisher('latitude_topic', Float64, queue_size=30)
    pub_longitude = rospy.Publisher('longitude_topic', Float64, queue_size=30)
    pub_utm_x = rospy.Publisher('utm_x', Float64, queue_size=30)
    pub_utm_y = rospy.Publisher('utm_y', Float64, queue_size=30) 
    rospy.Subscriber('nmea_sentence', Sentence, lambda msg: nmea_callback(msg, pub_heading, pub_latitude, pub_longitude, pub_utm_x, pub_utm_y))
    rospy.spin()

# NMEA 문장 파싱 및 GPS 데이터 추출 함수
def parse_nmea_sentence(nmea_sentence):
    parts = nmea_sentence.split(',')

    heading = None
    latitude = None
    longitude = None
    utm_coords = None

    # NMEA 문장 유형에 따라 파싱
    if parts[0] == "$GNHDT":
        heading = float(parts[1])
    elif parts[0] == "$GNGGA":
        if len(parts) > 4: # 데이터 완전성 검사
            latitude_data = parts[2]
            longitude_data = parts[4]

            # 위도와 경도를 도 단위로 변환
            latitude = float(latitude_data[:2]) + float(latitude_data[2:]) / 60
            longitude = float(longitude_data[:3]) + float(longitude_data[3:]) / 60

            if 'S' in latitude_data:
                latitude = -latitude
            if 'W' in longitude_data:
                longitude = -longitude

            # 위도와 경도를 UTM 좌표로 변환
            utm_coords = utm.from_latlon(latitude, longitude)

    return heading, latitude, longitude, utm_coords

# 콜백 함수
def nmea_callback(msg, pub_heading, pub_latitude, pub_longitude, pub_utm_x, pub_utm_y):
    nmea_sentence = msg.sentence
    heading, latitude, longitude, utm_coords = parse_nmea_sentence(nmea_sentence)
    if heading is not None:
        pub_heading.publish(heading)
        #print(f"Heading: {heading}")
    if latitude is not None and longitude is not None:
        pub_latitude.publish(latitude)
        pub_longitude.publish(longitude)
        print(f"__________________________________")
        print(f"Latitude: {latitude}\nLongitude: {longitude}")
    if utm_coords is not None:
        pub_utm_x.publish(utm_coords[0])
        pub_utm_y.publish(utm_coords[1])
        print(f"UTM X: {utm_coords[0]}\nUTM Y: {utm_coords[1]}")

if __name__ == '__main__':
    listener()
