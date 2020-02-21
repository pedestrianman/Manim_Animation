
from manimlib.imports import *
import os
import pyclbr
import numpy as np

class Orbiting(Group):
    CONFIG = {
        "rate": 7.5,
    }

    def __init__(self, planet, star, ellipse, **kwargs):
        Group.__init__(self, **kwargs)

        self.planet = planet
        self.star = star
        self.ellipse = ellipse
        self.time = 0
        
        # Proportion of the way around the ellipse
        self.proportion = 0
        planet.move_to(ellipse.point_from_proportion(0))
        self.add_updater(lambda m: m.update(dt))

    def update(self, dt):
        
        self.time += dt

        planet = self.planet
        star = self.star
        ellipse = self.ellipse
        
        rate = self.rate
        radius_vector = planet.get_center() - star.get_center()
        rate *= 1.0 / get_norm(radius_vector)

        prop = self.proportion
        d_prop = 0.001
        ds = get_norm(op.add(
            ellipse.point_from_proportion((prop + d_prop) % 1),
            -ellipse.point_from_proportion(prop),
        ))
        if self.time <= 10:
            rapidez = 8
        else: 
            rapidez = 65
        delta_prop = (d_prop / ds) * rate * rapidez * dt #El optimo es 8
        self.proportion = (self.proportion + delta_prop) % 1
        planet.move_to(
            ellipse.point_from_proportion(self.proportion)
        )


class SunAnimation(Group):
    CONFIG = {
        "rate": 0.2,
        "angle": 60 * DEGREES,
    }

    def __init__(self, sun, **kwargs):
        Group.__init__(self, **kwargs)
        self.sun = sun
        self.rotated_sun = sun.deepcopy()
        self.rotated_sun.rotate(60 * DEGREES)
        self.time = 0

        self.add(self.sun, self.rotated_sun)
        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt):
        time = self.time
        self.time += dt
        a = (np.sin(self.rate * time * TAU) + 1) / 2.0
        self.rotated_sun.rotate(-self.angle)
        self.rotated_sun.move_to(self.sun)
        self.rotated_sun.rotate(self.angle)
        self.rotated_sun.pixel_array = np.array(
            a * self.sun.pixel_array,
            dtype=self.sun.pixel_array.dtype
        )

class TheMotionOfPlanets(Scene):
    
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "random_seed": 2,
    }

    def construct(self):
        self.add_title()
        Twitter = TextMobject("@Inaki\\_Huarte",tex_to_color_map={"@Inaki\\_Huarte": YELLOW}).to_corner(DR, buff = 0.25)
        self.add(Twitter)
        self.setup_orbits()

    def add_title(self):
        title = TextMobject("``The motion of planets around the sun''")
        title.set_color(YELLOW)
        title.to_edge(UP)
        title.add_to_back(title.copy().set_stroke(BLACK, 5))
        # self.add(title)
        self.title = title

    def setup_orbits(self):

        sun = ImageMobject("sun")
        sun.set_height(0.7)
        
        self.add(SunAnimation(sun))
        planets, ellipses, orbits = self.get_planets_ellipses_and_orbits(sun)
        self.add(ellipses, planets)
        self.add(*orbits)
        self.add_foreground_mobjects(planets)

        self.wait(3)
        self.play(ApplyMethod(planets[0].set_opacity, 0.3), FadeOut(ellipses[0]),
                  ApplyMethod(planets[1].set_opacity, 0.3), FadeOut(ellipses[1]),
                  FadeOut(ellipses[2]),FadeOut(ellipses[3]))
        
        
        def update_line(line):
            new_line = Line(planets[2].get_center(),planets[-1].get_center())
            line.become(new_line).set_opacity(0.5)

        line = VGroup(Line(planets[2].get_center(),planets[-1].get_center()))
        line.set_stroke(width=0.7)
        self.add(line)
        line.add_updater(update_line).set_opacity(0.5)
        self.add(line)
        self.wait(1.5)
        dot = Dot(line.get_center(),color=RED)
        self.add(dot)
        
        #Path
        path = VMobject(color=RED)
        # Path can't have the same coord twice, so we have to dummy point
        path.set_points_as_corners([dot.get_center(),dot.get_center()+UP*0.001])
        self.add(path)
        # Path group
        path_group = VGroup(dot,path)
         # update function of path_group
        def update_group(group, line):
            dot,path = group
            dot.move_to(line.get_center())
            old_path = path.copy()
            old_path.append_vectorized_mobject(Line(old_path.points[-1],dot.get_center()))
            old_path.make_smooth()
            path.become(old_path)
        
        path_group.add_updater(lambda group: update_group(group,line))
        self.add(path_group)
    
        self.wait(80)
        
    def get_planets_ellipses_and_orbits(self, sun):
        planets = Group(
            ImageMobject("Mercurio"),
            ImageMobject("Venus"),
            ImageMobject("Tierra"),
            ImageMobject("Marte")
        )
        sizes = [0.383, 0.95, 1.0, 0.532]
        orbit_radii = [0.254, 0.475, 0.656, 1.0]
        orbit_eccentricies = [0.0, 0.0, 0.0, 0.0]

        for planet, size in zip(planets, sizes):
            planet.set_height(0.5)
            planet.scale(size)
                
        ellipses = VGroup(*[
            Circle(radius=r, color=WHITE, stroke_width=1)
            for r in orbit_radii
        ])
        
        for circle, ec in zip(ellipses, orbit_eccentricies):
            a = circle.get_height() / 2
            c = ec * a
            b = np.sqrt(a**2 - c**2)
            circle.stretch(b / a, 1)
            c = np.sqrt(a**2 - b**2)
            circle.shift(c * RIGHT)

        for circle in ellipses:
            circle.rotate(
                TAU * np.random.random(),
                about_point=ORIGIN
            )

        ellipses.scale(3.5, about_point=ORIGIN)
        
        orbits = [
            Orbiting(
                planet, sun, circle,
                rate=0.25 * r**(2 / 3)
            )
            for planet, circle, r in zip(planets, ellipses, orbit_radii)
        ]
       
        return planets, ellipses, orbits
