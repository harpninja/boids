'''
Vector class
Without numpy because Maya does not support it.
'''
# from __future__ import division
import math

class vec3(object):
    '''
    Three dimensional vector class.
    Complies with Python 2.7 conventions in Maya.
    Remove (object) for use in Python 3.0 code.
    '''
    def __init__(self, x, y, z):
        (self.x, self.y, self.z) = (x, y, z)
        self.values = (self.x, self.y, self.z)

    def __repr__(self):
        return str(self.x) + ', ' + str(self.y) + ', ' + str(self.z)

    def __getitem__(self, key):
        return self.values[key]

    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            # other is a vector
            return vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            # other is a scalar
            return vec3(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        if isinstance(other, self.__class__):
            # other is a vector
            return vec3(other.x * self.x, other.y * self.y, other.z * self.z)
        else:
            # other is a scalar
            return vec3(other * self.x, other * self.y, other * self.z)

    def __div__(self, other):
        if isinstance(other, self.__class__):
            # other is a vector
            return vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            return vec3(self.x / other, self.y / other, self.z / other)

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            # other is a vector
            return vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            # other is a scalar
            return vec3(self.x / other, self.y / other, self.z / other)

    def __abs__(self):
        '''
        Absolute value or magnitude of vector
        '''
        x = self.x**2
        y = self.y**2
        z = self.z**2
        return math.sqrt(x + y + z)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def limit(self, maximum):
        '''
        Magnitude of vector is limited to maximum.
        '''
        if self.squared_length() > math.pow(maximum, 2):
            normalised = self.unit_vector()
            self.x = normalised.x * maximum
            self.y = normalised.y * maximum
            self.z = normalised.z * maximum
        return self

    def unit_vector(self):
        '''
        Normalised vector or unit vector.
        '''
        magnitude = abs(self)
        if magnitude > 0.0:
            self.x = self.x / magnitude
            self.y = self.y / magnitude
            self.z = self.z / magnitude
            return self
        else:
            return vec3(0.0, 0.0, 0.0)

    def cosine_direction(self):
        '''
        Direction cosine of the given vector.
        Returns each direction cosine as degrees.
        '''
        cos_x = self.x / abs(self)
        cos_y = self.y / abs(self)
        cos_z = self.z / abs(self)

        x_rad = math.acos(cos_x)
        y_rad = math.acos(cos_y)
        z_rad = math.acos(cos_z)
        return (math.degrees(x_rad), math.degrees(y_rad), math.degrees(z_rad))

    def distance(self, other):
        '''
        Distance between two vectors
        '''
        distance_x = math.pow((self.x - other.x), 2)
        distance_y = math.pow((self.y - other.y), 2)
        distance_z = math.pow((self.z - other.z), 2)
        return math.sqrt(distance_x + distance_y + distance_z)

    def dot_product(self, other):
        '''
        Sum of products of unit vectors.
        '''
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross_product(self, other):
        '''
        New vector at right angles to self and other.
        '''
        self.x = (self.y * other.z) - (self.z * other.y)
        self.y = (self.z * other.x) - (self.x * other.z)
        self.z = (self.x * other.y) - (self.y * other.x)
        return self

    def squared_length(self):
        '''
        Squared length of self vector.
        Returns float.
        '''
        return self.x * self.x + self.y * self.y + self.z * self.z
