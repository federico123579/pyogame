import os
from random import randint

import pytest
from dotenv import load_dotenv

from pyogame.agent import OGame
from pyogame.constants import (
    buildings,
    coordinates,
    fleet,
    mission,
    price,
    research,
    resources,
    ships,
    speed,
    status,
)


def get_ogame():
    load_dotenv()
    return OGame(
        os.getenv("OGAME_UNI"),
        os.getenv("OGAME_USER"),
        os.getenv("OGAME_PASS"),
    )


class TestOGame:
    empire = get_ogame()
    ids = []

    def collect_all_ids(self):
        self.ids.extend(self.empire.planet_ids())
        self.ids.extend(self.empire.moon_ids())

    def test_Vars(self):
        assert isinstance(self.empire.token, str)

    def test_Events(self):
        assert isinstance(self.empire.attacked(), bool)
        assert isinstance(self.empire.neutral(), bool)
        assert isinstance(self.empire.friendly(), bool)

    def test_Constants(self):
        speed = self.empire.server().Speed
        assert speed.universe > 0
        assert speed.fleet > 0

        assert isinstance(self.empire.character_class(), str)

        assert isinstance(self.empire.rank(), int)

        assert len(self.empire.planet_ids()) > 0
        planets_names = self.empire.planet_names()
        assert len(planets_names) > 0
        assert isinstance(
            self.empire.id_by_planet_name(planets_names[0]), int
        )
        assert isinstance(self.empire.planet_coords(), list)
        assert len(self.empire.moon_ids()) > -1
        assert len(self.empire.moon_names()) > -1
        assert isinstance(self.empire.moon_coords(), list)

        self.collect_all_ids()

        assert buildings.is_supplies(buildings.metal_mine)
        assert buildings.building_name(buildings.metal_mine) == 'metal_mine'
        assert buildings.is_facilities(buildings.shipyard)
        assert buildings.is_defenses(buildings.rocket_launcher(10))
        assert buildings.defense_name(buildings.rocket_launcher()) == 'rocket_launcher'
        assert research.is_research(research.energy)
        assert research.research_name(research.energy) == 'energy'
        assert ships.is_ship(ships.small_transporter(99))
        assert ships.ship_name(ships.light_fighter()) == 'light_fighter'
        assert ships.ship_amount(ships.light_fighter(99)) == 99
        assert resources(99, 99, 99) == [99, 99, 99]
        assert [3459, 864, 0] == price(buildings.metal_mine, level=10)

    def test_slot_celestial(self):
        slot = self.empire.slot_celestial()
        assert slot.total > 0

    def test_celestial(self):
        celestial = self.empire.celestial(id)
        assert celestial.diameter > 0
        assert celestial.free > -1
        assert isinstance(celestial.temperature, list)

    def test_celestial_coordinates(self):
        for id in self.ids:
            celestial_coordinates = self.empire.celestial_coordinates(id)
            assert isinstance(celestial_coordinates, list)
            assert len(celestial_coordinates) == 4

    def test_celestial_queue(self):
        for id in self.ids:
            celestial_queue = self.empire.celestial_queue(id)
            assert isinstance(celestial_queue.list, list)

    def test_resources(self):
        for id in self.ids:
            res = self.empire.resources(id)
            assert isinstance(res.resources, list)
            assert res.darkmatter > 0
            assert isinstance(res.energy, int)

    def test_resources_settings(self):
        settings = self.empire.resources_settings(
            self.ids[0],
            settings={buildings.metal_mine: speed.min}
        )
        assert settings.metal_mine == 10
        settings = self.empire.resources_settings(
            self.ids[0],
            settings={buildings.metal_mine: speed.max}
        )
        assert settings.metal_mine == 100

    def test_supply(self):
        sup = self.empire.supply(self.ids[0])
        assert 0 < sup.metal_mine.level

    def test_facilities(self):
        fac = self.empire.facilities(self.ids[0])
        assert 0 < fac.robotics_factory.level

    def test_moon_facilities(self):
        fac = self.empire.moon_facilities(self.ids[0])
        assert 0 < fac.robotics_factory.level

    def test_research(self):
        res = self.empire.research()
        assert res.energy.level > -1

    def test_ships(self):
        ship = self.empire.ships(self.ids[0])
        assert ship.light_fighter.amount > -1

    def test_defences(self):
        defence = self.empire.defences(self.ids[0])
        assert defence.rocket_launcher.amount > -1

    def test_galaxy(self):
        for position in self.empire.galaxy(coordinates(1, 1)):
            assert isinstance(position.player, str)
            assert isinstance(position.list, list)
            assert isinstance(position.moon, bool)

    def test_galaxy_debris(self):
        for position in self.empire.galaxy_debris(coordinates(1, 1)):
            assert isinstance(position.position, list)
            assert isinstance(position.has_debris, bool)
            assert isinstance(position.metal, int)
            assert position.deuterium == 0

    def test_ally(self):
        assert isinstance(self.empire.ally(), list)

    def test_slot_fleet(self):
        slot = self.empire.slot_fleet()
        assert slot.fleet.total > 0

    @pytest.mark.social
    def test_fleet(self):
        self.test_send_fleet()
        for fl in self.empire.fleet():
            assert isinstance(fl.id, int)
            if fl.mission == mission.spy:
                assert fl.mission == mission.spy

    @pytest.mark.social
    def test_return_fleet(self):
        self.test_send_fleet()
        for fl in self.empire.fleet():
            if fl.mission == mission.spy and not fl.returns:
                fleet_returning = self.empire.return_fleet(fl.id)
                assert fleet_returning

    @pytest.mark.dirty
    def test_build(self):
        before = self.empire.defences(
            self.ids[0]
        ).rocket_launcher.amount
        self.empire.build(
            what=buildings.rocket_launcher(),
            id=self.empire.planet_ids()[0]
        )
        after = self.empire.defences(
            self.ids[0]
        ).rocket_launcher
        assert before < after.amount or after.in_construction

    @pytest.mark.dirty
    def test_deconstruct_and_cancel(self):
        before = self.empire.supply(
            self.ids[0]
        ).metal_mine
        assert before.level > 0
        assert not before.in_construction
        self.empire.deconstruct(
            what=buildings.metal_mine,
            id=self.ids[0]
        )
        after = self.empire.supply(
            self.ids[0]
        ).metal_mine
        assert before.level > after.level or after.in_construction
        before = self.empire.supply(
            self.ids[0]
        ).metal_mine
        assert before.in_construction
        self.empire.cancel_building(self.ids[0])
        after = self.empire.supply(
            self.ids[0]
        ).metal_mine
        assert not after.in_construction

    def test_phalanx(self):
        pass

    @pytest.mark.slow
    @pytest.mark.social
    def test_send_message(self):
        send_message = False
        while not send_message:
            for position in self.empire.galaxy(
                    coordinates(randint(1, 6), randint(1, 499))
            ):
                if status.inactive in position.status:
                    send_message = self.empire.send_message(
                        position.player_id,
                        'Hello'
                    )
                    break
        assert send_message

    def test_spyreports(self):
        for report in self.empire.spyreports():
            assert isinstance(report.name, str)
            assert isinstance(report.position, list)
            assert isinstance(report.metal, int)
            assert isinstance(report.resources, list)
            assert isinstance(report.fleet, dict)

    @pytest.mark.social
    def test_send_fleet(self):
        espionage_probe = self.empire.ships(self.ids[0]).espionage_probe.amount
        if not 0 < espionage_probe:
            self.empire.build(ships.espionage_probe(), self.ids[0])
            while self.empire.ships(self.ids[0]).espionage_probe.amount == 0:
                continue

        fleet_send = True
        while not fleet_send:
            for planet in self.empire.galaxy(
                    coordinates(randint(1, 6), randint(1, 499))
            ):
                if status.inactive in planet.status \
                        and status.vacation not in planet.status:
                    fleet_send = self.empire.send_fleet(
                        mission.spy,
                        self.ids[0],
                        where=planet.position,
                        ships=fleet(espionage_probe=1)
                    )
                    break
        assert fleet_send

    def test_collect_rubble_field(self):
        self.empire.collect_rubble_field(self.ids[0])

    def test_relogin(self):
        self.empire.logout()
        self.empire.relogin()
        assert self.empire.is_logged_in()

    def test_officers(self):
        officers = self.empire.officers()
        assert isinstance(officers.commander, bool)
        assert isinstance(officers.admiral, bool)
        assert isinstance(officers.engineer, bool)
        assert isinstance(officers.geologist, bool)
        assert isinstance(officers.technocrat, bool)
