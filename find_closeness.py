import json
import fileinput
import csv
import math
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

#constant
checking_time=True

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

def datetimeToMin(dt):
  return tDiff(dt,datetime.fromtimestamp(0))

def tDiff(t1,t2):
  t1 = t1
  t2  = t2
  minutes  = math.floor((abs(t1 - t2).seconds) / 60)
  return minutes

class Trip:
  def __init__(self, trip_id, vehicle_id, start_time, end_time, lat, lon, lat2, lon2):
    self.trip_id = trip_id
    self.vehicle_id = vehicle_id
    self.start_time = start_time
    self.end_time = end_time
    #date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    self.start_time_obj = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
    self.end_time_obj = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')

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

  def for_darwin(self):
    """http://www.darrinward.com/lat-long/"""
    return '{},{}\n{},{}'.format(self.start_lat, self.start_lon, self.end_lat, self.end_lon)

  def get_id(self):
    return str(self.vehicle_id) + '#' + str(self.trip_id)


  def __str__(self):
    if checking_time:
      return 'Id: {} Trip start: {}, {} {} End {}, {} {}'.format(self.get_id(), self.start_time, self.start_lat, self.start_lon, self.end_time, self.end_lat, self.end_lon)
    else:
      return 'Id: {} Trip start: {} {} End {} {}'.format(self.get_id(), self.start_lat, self.start_lon, self.end_lat, self.end_lon)

  @staticmethod
  def serialize(self):
      return {
          "id": self.get_id(),
          "vehicle_id": self.vehicle_id,
          "trip_id":   self.trip_id,
          "start_time": self.start_time,
          "end_time": self.end_time,
          "start_lat": self.start_lat,
          "end_lat": self.end_lat,
          "start_lon": self.start_lon,
          "end_lon": self.end_lon
      }

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
  is_close = extra < .25 * trip.get_distance()
  is_close = is_close or extra < 5
  is_same = trip.vehicle_id == trip2.vehicle_id



  is_similar_time=True

  if checking_time:
    # print datetimeToMin(trip.start_time_obj)
   # if tDiff(trip.start_time_obj,trip2.start_time_obj)>30 and tDiff(trip.end_time_obj,trip2.end_time_obj)>30:
    if datetimeToMin(trip.start_time_obj)-30<datetimeToMin(trip2.start_time_obj) and datetimeToMin(trip.end_time_obj)+30>datetimeToMin(trip2.end_time_obj):
      is_similar_time=False



  #   print get_starts_distance(trip, trip2), get_ends_distance(trip, trip2), trip2.get_distance()
  #   print get_pickup_distance(trip, trip2), trip.get_distance()
  #   return True
  # return False
  return is_close and not is_same and (not checking_time or is_similar_time)

trips = readtrips()

count = 0

matches = {}
all_trips = {}
extra_kms = {}
for trip in trips:
  best = 1e20
  best_trip = None
  for trip2 in trips:
    if trip != trip2:
      if should_carpool(trip, trip2):
        extra = get_extra_distance(trip, trip2)
        if extra < best:
          best_trip = trip2
          best = extra
        # matches.append((trip,trip2,extra));
        # print 'match', count, trip, trip2, "Extra:",extra
        # print 'DARWIN'
        # print trip.for_darwin()
        # print trip2.for_darwin()
  if best_trip:
    matches[trip.get_id()] = best_trip
    extra_kms[trip.get_id()] = best
    count += 1
  all_trips[trip.get_id()] = trip

out_json = json.dumps([matches, all_trips, extra_kms], default=Trip.serialize)
with open('best-rides.json', 'w') as f:
  f.write(out_json)
print count