// Copyright 2011 (c) The Native Client Authors.  All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/**
 * @file
 * The JavaScript simulation of the flocking algorithm.  Owns an array of
 * geese, and runs the flocking simulation that computes new goose locations.
 */

goog.provide('Flock');

goog.require('Goose');
goog.require('goog.Disposable');
goog.require('goog.array');

/**
 * Constructor for the Flock class.
 * @constructor
 * @extends {goog.Disposable}
 */
Flock = function() {
  goog.Disposable.call(this);

  /**
   * The flock of geese.
   * @type {Array.<Goose>}
   * @private
   */
  this.geese_ = [];
}
goog.inherits(Flock, goog.Disposable);

/**
 * Override of disposeInternal() to dispose of retained objects.
 * @override
 */
Flock.prototype.disposeInternal = function() {
  Flock.superClass_.disposeInternal.call(this);
}

/**
 * Create a flock of geese.  The geese start at the given location with
 * random velocities.  Any previous geese are deleted and the simulation
 * starts with an entirely new flock.
 * @param {!number} size The size of the flock.
 * @param {?goog.math.Vec2} opt_initialLocation The initial location of each
 *     goose in the flock.
 */
Flock.prototype.resetFlock = function(size, opt_initialLocation) {
  goog.array.clear(this.geese_);
  var initialLocation = opt_initialLocation || new goog.math.Vec2(0, 0);
  for (var goose = 0; goose < size; goose++) {
    this.geese_[goose] = new Goose(initialLocation);
  }
}

/**
 * Run one tick of the simulation, recording the time.
 * @param {?goog.math.Rect} opt_flockBox The geese will stay inside of this
 *     box.  If the parameter is not given, the geese don't have boundaries.
 * @return {number} the simulation tick duration in miliseconds.
 */
Flock.prototype.flock = function(opt_flockBox) {
  var flockBox = opt_flockBox || new goog.math.Rect(0, 0, 200, 200);
  var clockStart = new Date().getTime();
  for (var goose = 0; goose < this.geese_.length; goose++) {
    this.geese_[goose].simulationTick(this.geese_, flockBox);
  }
  var clockEnd = new Date().getTime();
  var dt = clockEnd - clockStart;
  if (dt < 0) {
    dt = 0;  // Just in case.
  }
  return dt;
}

/**
 * Render the flock into the given canvas.
 * @param {!Canvas} canvas The target canvas.
 */
Flock.prototype.render = function(canvas) {
  for (var goose = 0; goose < this.geese_.length; goose++) {
    this.geese_[goose].render(canvas);
  }
}