import argparse

import numpy as np

import sc2
from sc2 import Race, Difficulty, run_game, maps, Result, position
from sc2.ids.buff_id import BuffId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer

from sc2.constants import PROBE, OBSERVER
from sc2.constants import NEXUS, ROBOTICSFACILITY, PYLON, ASSIMILATOR

class SquinnBot(sc2.BotAI):

    def __init__(self):
        self.time = 0
        self.nexus_limit = 3
        self.scout_locations = [self.enemy_start_locations[0]]
        self.distance_to_locindex = {}
        for index, el in enumerate(self.expansion_locations().keys()):
            dist = el.distance_to(self.scout_locations[0])
            self.dist_to_locindex[dist] = index + 1
            self.scout_locations.append(el)
        print(self.scout_locations)
        self.scouts = {}

    # def on_end(self, game_result):
    #     print("--- GAME OVER MAN ---")
    #     print(game_result)


    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("glhf nubcake")

        self.time = (self.state.game_loop / 22.4) / 60 # because reasons

        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()

        await self.expand()

    def _scouts_needed(self):
        if len(self.units(ROBOTICSFACILITY).ready) == 0:
            unit_type = PROBE
            unit_limit = 1
        else:
            unit_type = OBSERVER
            unit_limit = len(self.scout_location) / 2
        return unit_limit, unit_type

    async def scout(self):
        # First, check if we need to build any.
        n_scout, scout_type = self._scouts_needed()
        while len(self.scouts.keys() < n_scout):
            print("-- need {} scouts --".format(n_scout - len(self.scouts.keys())))
            unit = await self.build_scout(scout_type)
            self.scouts[unit.tag] = None

        # Move the ones that can be moved.
        lolded = []
        for scout_tag in scouts.keys():
            # Get the scout.
            scout = self.units.owned.find_by_tag(scout_tag)
            if scout is None:  # lol ded
                lolded.append(scout_tag)
                continue
            if not scout.is_ready: continue  # Might still be building.
            
            # Move it somewhere.
            pos = scouts[scout_tag]
            if pos is None:
                # Get the next unassigned enemy location.
                

        
    async def build_scout(self, unit_type):
        new_unit = None
        if unit_type == PROBE:
            await self.build_workers()
            return workers.random.first
        else:
            for rf in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.can_afford(OBSERVER) and self.supply_left > 0:
                    await self.do(rf.train(OBSERVER))
                    return self.units(OBSERVER).random.first


    async def build_workers(self):
        if self.workers.amount < (self.units(NEXUS).amount * 22) + 1:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        abilities = await self.get_available_abilities(nexus)
                        if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                            await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                    await self.do(nexus.train(PROBE))
                else:
                    break

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists and self.can_afford(PYLON):
                await self.build(PYLON,
                    near = self.units(NEXUS).first.position.towards(self.game_info.map_center, 5))

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            geysers = self.state.vespene_geyser.closer_than(15.0, nexus)
            for geyser in geysers:
                if self.can_afford(ASSIMILATOR):
                    worker = self.select_build_worker(geyser.position)
                    if worker is not None and \
                            not self.units(ASSIMILATOR).closer_than(1.0, geyser).exists:
                        await self.do(worker.build(ASSIMILATOR, geyser))

    async def expand(self):
        try:
            if self.units(NEXUS).amount < self.nexus_limit and self.can_afford(NEXUS):
                await self.expand_now()
        except Exception as e:
            print(str(e))
    
if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(description = "The Squinn Bot")
    parser.add_argument("--race", choices = ["protoss", "zerg", "terran", "random"], 
        default = "random", help = "Specify the race [DEFAULT: random]")
    parser.add_argument("--seed", type = int, default = 42,
        help = "Random seed [DEFAULT: 42].")
    parser.add_argument("--headless", action = "store_true")
    args = vars(parser.parse_args())

    np.random.seed(args['seed'])
    races = {"protoss": Race.Protoss, "terran": Race.Terran, "zerg": Race.Zerg}
    if args['race'] == "random":
        race = np.random.choice(list(races.values()))
    else:
        race = races[args['race']]
    """

    run_game(maps.get("AbyssalReefLE"), [
        Bot(Race.Protoss, SquinnBot()),
        Computer(Race.Terran, Difficulty.Easy)
    ], realtime = True)
