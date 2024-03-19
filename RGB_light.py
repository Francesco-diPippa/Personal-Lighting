import sys
from xknx import XKNX
from xknx.devices import Light
import asyncio
import multiprocessing


class RGBLight:
    def __init__(self):
        self.name = 'RGBWLight'
        self.group_address_switch = "0/0/3"
        self.group_address_switch_state = "0/1/2"
        self.group_address_brightness_red = "0/3/2"
        self.group_address_switch_state_red = "1/0/0"
        self.group_address_brightness_state_red = "1/0/1"
        self.group_address_brightness_green = "0/3/3"
        self.group_address_switch_state_green = "1/0/2"
        self.group_address_brightness_state_green = "1/0/3"
        self.group_address_brightness_blue = "0/3/4"
        self.group_address_switch_state_blue = "1/0/4"
        self.group_address_brightness_state_blue = "1/0/5"
        self.group_address_switch_white = "0/0/8"""
        self.isOn = False

        self.jobs = multiprocessing.JoinableQueue()
        self._crea_processi(self.jobs, 5)

    def _crea_processi(self, jobs, concorrenza):
        for _ in range(concorrenza):
            proc = multiprocessing.Process(None, target=self._call_update, args=(jobs,))
            proc.daemon = True
            proc.start()

    def change_color(self, color=None):
        print('changing color ' + str(color))
        self.jobs.put(color)
        print(self.jobs)
        #asyncio.run(self._update_light(color))

    def set_off(self):
        asyncio.run(self._update_light(turn_on=False))

    def _call_update(self, jobs):
        while True:
            color = jobs.get()
            asyncio.run(self._update_light(color))

    async def _update_light(self, color=None, turn_on=True):
        try:
            async with XKNX() as xknx:
                light = Light(xknx,
                              name=self.name,
                              group_address_switch=self.group_address_switch,
                              group_address_brightness_red=self.group_address_brightness_red,
                              group_address_brightness_green=self.group_address_brightness_green,
                              group_address_brightness_blue=self.group_address_brightness_blue,
                              group_address_switch_white=self.group_address_switch_white
                              )

                if turn_on and color:
                    await light.sync()
                    # print(light.state)
                    if not self.isOn:
                        await light.set_on()
                        # await light.set_color((255, 255, 255))
                        await asyncio.sleep(3)
                        await light.set_color(color)
                        self.isOn = True
                    else:
                        # await light.set_color((255, 255, 255))
                        await asyncio.sleep(1)
                        await light.set_color(color)
                elif not turn_on:
                    await light.set_off()
                    await light.set_color((0, 0, 0))
                    self.isOn = False

        except Exception as e:
            print(e)
            sys.exit()
