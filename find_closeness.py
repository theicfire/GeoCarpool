import fileinput

def distance(lat, lon, endlat, endlon):
  return (lat - endlat) ** 2 + (lon - endlon) ** 2

class Trip:
  def __init__(self, lat, lon, lat2, lon2):
    self.start_lat = float(lat)
    self.start_lon = float(lon)
    self.end_lat = float(lat2)
    self.end_lon = float(lon2)

  def get_distance(self):
    return distance(self.start_lat, self.start_lon, self.end_lat, self.end_lon)

  def __str__(self):
    return 'Trip start: {} {} End {} {}'.format(self.start_lat, self.start_lon, self.end_lat, self.end_lon)


def readlines(f):
  trips = []
  for line in fileinput.input(f):
    line = line.strip()
    print line.split(',')
    lat, lon, end_lat, end_lon = line.split(',')
    trips.append(Trip(lat, lon, end_lat, end_lon))
  return trips

trips = readlines('latlongboth')

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
  return extra < .25 * trip.get_distance()

count = 0
for trip in trips:
  for trip2 in trips:
    if trip != trip2:
      if should_carpool(trip, trip2):
        print 'match', count, trip, trip2
        count += 1

