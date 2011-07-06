# ###################################################
# Copyright (C) 2011 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import horizons.main

from fife import fife
from horizons.constants import GAME_SPEED, LAYERS
from horizons.scheduler import Scheduler
from horizons.util import WorldObject

class Bullet(WorldObject):
	"""
	Class for Bullet animation
	"""
	is_selectable = False
	def __init__(self, image, source, dest, speed, session):
		"""
		@param image: path to file with bullet image
		@param source: Point with starting position
		@param dest: Point with ending position
		@param speed: Attack speed of the Weapon that fires the canonball
		@param session: Horizons Session
		"""

		super(Bullet, self).__init__()
		self.session = session
		# get the current position
		self.x = source.x
		self.y = source.y
		# offset the position so it starts from the middle of the firing instance
		self.x += 1
		self.y -= 1
		# needed ticks to go to the destination
		self.needed_ticks = int(GAME_SPEED.TICKS_PER_SECOND * source.distance(dest) / speed)
		self.needed_ticks -= 2
		# the thick that the object is currently at
		self.current_tick = 0
		# calculate the axis ratio that is added per tick to move
		self.x_ratio = float(dest.x - source.x)/self.needed_ticks
		self.y_ratio = float(dest.y - source.y)/self.needed_ticks

		self._object = horizons.main.fife.engine.getModel().createObject(str(self.worldid), 'cannonball')
		fife.ObjectVisual.create(self._object)
		visual = self._object.get2dGfxVisual()
		img = horizons.main.fife.imagepool.addResourceFromFile(image)
		for rotation in [45, 135, 225, 315]:
			visual.addStaticImage(rotation, img)
		coords = fife.ModelCoordinate(int(self.x), int(self.y))
		coords.thisown = 0
		self._instance = session.view.layers[LAYERS.OBJECTS].createInstance(self._object, coords)
		self._instance.setId(str(self.worldid))
		fife.InstanceVisual.create(self._instance)

		loc = fife.Location(session.view.layers[LAYERS.OBJECTS])
		loc.thisown = 0
		coords = fife.ModelCoordinate(int(dest.x), int(dest.y))
		coords.thisown = 0
		loc.setLayerCoordinates(coords)
		self._instance.setLocation(loc)
		self.session.world.bullets.append(self)

		self._move_tick()

	def _move_tick(self):
		if self.current_tick == self.needed_ticks:
			self._instance.getLocationRef().getLayer().deleteInstance(self._instance)
			self._instance = None
			self.session.world.bullets.remove(self)
			self.remove()
			return
		self.current_tick += 1
		self.x += self.x_ratio
		self.y += self.y_ratio

		loc = self._instance.getLocation()
		coords = loc.getMapCoordinates()
		coords.x = self.x
		coords.y = self.y
		loc.setMapCoordinates(coords)
		self._instance.setLocation(loc)

		Scheduler().add_new_object(self._move_tick, self, 1)

	def save(self, db):
		#TODO 
		pass
