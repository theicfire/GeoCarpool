

import fileinput
import csv
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km


def distance(lat, lon, endlat, endlon):
  # return sqrt((lat - endlat) ** 2 + (lon - endlon) ** 2)
  return haversine(lon, lat, endlon, endlat)



class Trip:
  def __init__(self, trip_id, vehicle_id, start_time, end_time, lat, lon, lat2, lon2):
    self.trip_id = trip_id
    self.vehicle_id = vehicle_id
    self.start_time = start_time
    self.end_time = end_time
    self.start_lat = float(lat)
    self.start_lon = float(lon)
    self.end_lat = float(lat2)
    self.end_lon = float(lon2)

  def get_distance(self):
    return distance(self.start_lat, self.start_lon, self.end_lat, self.end_lon)

  def is_valid(self):
    return abs(self.start_lat) > 0 \
      and abs(self.end_lat) > 0 \
      and abs(self.start_lon) > 0 \
      and abs(self.end_lon) > 0 \
      and self.get_distance() > 1e-9

  def __str__(self):
    return 'Id: {} Vehicle: {} Trip start: {} {} End {} {}'.format(self.trip_id, self.vehicle_id, self.start_lat, self.start_lon, self.end_lat, self.end_lon)

def readtrips():
  trips = []
  skip = True
  with open('othertrip.csv', 'rb') as csvfile:
      reader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in reader:
        if skip:
          skip = False
          continue
        idtrips, idvehicles, starttime, endtime, start_lon, end_lon, start_lat, end_lat = row
        trip = Trip(idtrips, idvehicles, starttime, endtime, start_lat, start_lon, end_lat, end_lon)
        if trip.is_valid():
          trips.append(trip)
  return trips

def get_pickup_distance(trip, trip2):
  return get_starts_distance(trip, trip2) + get_ends_distance(trip, trip2) + trip2.get_distance()

def get_starts_distance(trip, trip2):
  return distance(trip.start_lat, trip.start_lon, trip2.start_lat, trip2.start_lon)

def get_ends_distance(trip, trip2):
  return distance(trip.end_lat, trip.end_lon, trip2.end_lat, trip2.end_lon)

def get_extra_distance(trip, trip2):
  return get_pickup_distance(trip, trip2) - trip.get_distance()


def should_carpool(trip, trip2):
  extra = get_extra_distance(trip, trip2)
  assert(extra > -1e20)
  # is_close = extra < .25 * trip.get_distance()
  is_close = extra < 1
  is_same = trip.vehicle_id == trip2.vehicle_id
  # if is_close and not is_same:
  #   print get_starts_distance(trip, trip2), get_ends_distance(trip, trip2), trip2.get_distance()
  #   print get_pickup_distance(trip, trip2), trip.get_distance()
  #   return True
  # return False
  return is_close and not is_same

trips = readtrips()

count = 0
for trip in trips:
  for trip2 in trips:
    if trip != trip2:
      if should_carpool(trip, trip2):
        extra = get_extra_distance(trip, trip2)
        print 'match', count, trip, trip2, "Extra:",extra
        count += 1