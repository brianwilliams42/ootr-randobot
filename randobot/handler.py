from racetime_bot import RaceHandler, monitor_cmd, can_moderate, can_monitor
import random

class RandoHandler(RaceHandler):
    """
    RandoBot race handler. Generates seeds, presets, and frustration.
    """
    stop_at = ['cancelled', 'finished']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def begin(self):
        """
        Send introduction messages.
        """
        if self.should_stop():
            return
        if not self.state.get('intro_sent') and not self._race_in_progress():
            goal_name = self.data.get('goal', {}).get('name')
            if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
                await self.send_message(
                    'Welcome to DWR! Create a standard seed with !roll or !roll3 for version 3.0'
                )
            else:
                await self.send_message(
                    'Welcome to DWR! Create a custom flag seed with !dwflags <flags> or !dwflags3 <flags> for version 3.0'
                )
            await self.send_message(
                'Full list of raceroom commands at https://pastebin.com/raw/4nKVRxXR'
            )
            self.state['intro_sent'] = True
        if 'locked' not in self.state:
            self.state['locked'] = False

        self.state['seed_rolled'] = False
        self.state['build_type'] = 'release'

    @monitor_cmd
    async def ex_lock(self, args, message):
        """
        Handle !lock commands.

        Prevent seed rolling unless user is a race monitor.
        """
        self.state['locked'] = True
        await self.send_message(
            'Lock initiated. I will now only roll seeds for race monitors.'
        )

    @monitor_cmd
    async def ex_unlock(self, args, message):
        """
        Handle !unlock commands.

        Remove lock preventing seed rolling unless user is a race monitor.
        """
        if self._race_in_progress():
            return
        self.state['locked'] = False
        await self.send_message(
            'Lock released. Anyone may now roll a seed.'
        )

    async def ex_dwflags(self, args, message):
        await self.ex_dwflags3(args, message);

    async def ex_dwflags3(self, args, message):
        """
        Handle !dwflags3 commands.
        """
        if self._race_in_progress():
            return
        if not self.state.get('race_version'):
            self.state['race_version'] = 'v3.0.3'
        await self.roll_and_send_v3(args, message)

    async def ex_version(self, args, message):
        """
        Handle !version commands. Must start with "v" and can be 
        executed before or after rolling the seed.
        """
        if self._race_in_progress():
            return
        if len(args) != 1:
            await self.send_message('Hey, you forgot a new version.')
            return

        words = message.get('message', '').split(' ')
        version = words[1]
        if (version.startswith('v') == False):
            await self.send_message('Versions must start with "v" (ex.: "v2.2")')
            return
        self.state['race_version'] = version
        await self.send_message('Seed version updated to: {}'.format(version))
        await self.update_info()

    async def ex_beta(self, args, message):
        """
        Handle !beta commands. Requires a version and build number.
        Version starts with "v" and this command can be 
        executed before or after rolling the seed.
        """
        if self._race_in_progress():
            return
        if len(args) != 2:
            await self.send_message('Hey, you forgot a new version and build number.')
            await self.send_message('Example: !beta v3.0.3 670')
            return

        words = message.get('message', '').split(' ')
        if (words[1].startswith('v') == False):
            await self.send_message('Versions must start with "v" (ex.: "v2.2")')
            return
        await self.set_beta(words[1:])


    async def set_beta(self, words):
        """
        Sets the beta active and with the given version in words.
        """
        version = words[0] + 'b' + words[1]
        self.state['race_version'] = version
        self.state['build_type'] = 'beta'
        await self.send_message('Seed version updated to: {}'.format(version))
        await self.update_info()

    async def ex_url(self, args, message):
        await self.print_url()

    async def ex_clear(self, args, message):
        """
        Clears seed and flag from internal state and raceroom info.
        """
        if self._race_in_progress():
            return
        await self.clear()

    async def ex_roll(self, args, message):
        await self.ex_roll3(args, message);

    async def ex_roll3(self, args, message):
        """
        Rolls a new seed with the room default flags for version 3.0.
        """
        reply_to = message.get('user', {}).get('name')
        if self._race_in_progress():
            return
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags'):
            self.state['race_version'] = 'v3.0.3'
            await self.roll(
                flags="IVIAAVCEKACAAAAAAAAAAEAQ",
                reply_to=reply_to,
            )
        else:
            await self.send_message('This command only works in Standard')

    async def ex_summer(self, args, message):
        """
        Rolls a new seed with the room default flags for version 3.0.
        """
        reply_to = message.get('user', {}).get('name')
        if self._race_in_progress():
            return
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
            self.state['race_version'] = 'v2025-TE'
            self.state['build_type'] = 'te'
            await self.roll(
                flags="IVIAAVCEKACAAAAAAAAAAEAQ",
                reply_to=reply_to,
            )
        else:
            await self.send_message('This command only works in Standard and Tournament')

    async def ex_juef(self, args, message):
        """
        Rolls a new seed with the provided flags for a juef-build race.
        """
        reply_to = message.get('user', {}).get('name')
        if self._race_in_progress():
            return
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
            self.state['race_version'] = 'v3.0.3.18'
            self.state['build_type'] = 'juef'
            await self.roll_and_send_v3(args, message)
        else:
            await self.send_message('This command only works in Standard and Tournament')

    async def ex_week1(self, args, message):
        """
        Rolls a new seed with the week 1 2024 winter league flags.
        """
        await self.roll3nonstandard('CVKQAVCECUABCQAAIAAAAZAQ', 'It`s Winter Chaos Time', args, message)

    async def ex_week2(self, args, message):
        """
        Rolls a new seed with the week 2 2024 winter league flags.
        """
        await self.roll3nonstandard('IVIAAVCFKECBAQCAKEAAAZBU', 'Big Swamp? No Hurtmore? No Problem!', args, message)

    async def ex_week3(self, args, message):
        """
        Rolls a new seed with the week 3 2024 winter league flags.
        """
        await self.roll3nonstandard('IQAAAVCUAAABAAIAIAAAAIAQ', 'Neapolitan-ish', args, message)

    async def ex_week4(self, args, message):
        """
        Rolls a new seed with the week 4 2024 winter league flags.
        """
        await self.roll3nonstandard('UWVIA2CEVIUBVAAKUIAABWQQ', 'Random%', args, message)

    async def ex_week5(self, args, message):
        """
        Rolls a new seed with the week 5 2024 winter league flags.
        """
        await self.roll3nonstandard('KVIUAVCEKUABAAAAIAAAAFJU', 'ChaosThe2nd', args, message)

    async def ex_week6(self, args, message):
        """
        Rolls a new seed with the week 6 2024 winter league flags.
        """
        await self.roll3nonstandard('KVIAIVCFKUABAAAAIAAAAEJU', 'Stair Shuffle Chaos', args, message)

    async def ex_week7(self, args, message):
        """
        Rolls a new seed with the week 7 2024 winter league flags.
        """
        await self.roll3nonstandard('UWJIAVCVSJCBAAAAMAAAAGRU', 'Random Repel Runback', args, message)

    async def ex_week8a(self, args, message):
        """
        Rolls a new seed with the week 8a 2024 winter league flags.
        """
        await self.roll3nonstandard('IVIAAVCAKACBAACVCQAAAEJE', 'You No Nothing, Jon Snow', args, message)

    async def ex_week8b(self, args, message):
        """
        Rolls a new seed with the week 8b 2024 winter league flags.
        """
        await self.roll3nonstandard('KVIUIVCEKVABAAAAKEAAAEJU', 'Kitchen Sink!', args, message)

    async def roll3nonstandard(self, setflags, weekmsg, args, message):
        """
        Rolls a new seed with the room default flags for version 3.0.
        """
        reply_to = message.get('user', {}).get('name')
        
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
            await self.send_message('This does not work in Standard or Standard Tournament')
        else:
            if not self.state.get('race_version'):
                self.state['race_version'] = 'v3.0.3'
            await self.send_message(weekmsg)
            await self.roll(
                flags=setflags,
                reply_to=reply_to,
            )

    async def roll_and_send(self, args, message):
        """
        Read an incoming !dwflags command, and generate a new seed if
        valid.
        """
        reply_to = message.get('user', {}).get('name')

        if len(args) != 1:
            await self.send_message('Hey, you forgot flags.')
            return
        if self.state.get('locked') and not can_monitor(message):
            await self.send_message(
                'Sorry %(reply_to)s, seed rolling is locked. Only race '
                'monitors may roll a seed for this race.'
                % {'reply_to': reply_to or 'friend'}
            )
            return
        if self.state.get('seed_rolled') and not can_moderate(message):
            await self.send_message(
                'Well excuuuuuse me princess, but I already rolled a seed. '
                'Don\'t get greedy!'
            )
            return

        words = message.get('message', '').split(' ')

        await self.roll(
            flags=words[1],
            reply_to=reply_to,
        )

    async def roll_and_send_v3(self, args, message):
        """
        Read an incoming !dwflags command, and generate a new seed if
        valid.
        """
        reply_to = message.get('user', {}).get('name')

        if len(args) != 1:
            await self.send_message('Hey, you forgot flags.')
            return
        if self.state.get('locked') and not can_monitor(message):
            await self.send_message(
                'Sorry %(reply_to)s, seed rolling is locked. Only race '
                'monitors may roll a seed for this race.'
                % {'reply_to': reply_to or 'friend'}
            )
            return
        if self.state.get('seed_rolled') and not can_moderate(message):
            await self.send_message(
                'Well excuuuuuse me princess, but I already rolled a seed. '
                'Don\'t get greedy!'
            )
            return

        words = message.get('message', '').split(' ')

        await self.roll(
            flags=words[1],
            reply_to=reply_to,
        )

    async def roll(self, flags, reply_to):
        """
        Roll a new seed and update the race info.
        """
        if (self.state['seed_rolled']):
          await self.send_message('Seed already rolled! Use !clear before re-rolling.')
          return

        self.state['race_seed'] = random.randint(1000000000000, 10000000000000)
        self.state['seed_rolled'] = True
        self.state['race_flagstring'] = flags
        await self.update_info()

    async def clear(self):
        if (self.state['seed_rolled']):
          await self.set_raceinfo('', overwrite=True)
        self.state['seed_rolled'] = False
        self.state['race_flagstring'] = ''
        self.state['race_seed'] = 0
        self.state['race_version'] = ''
        self.state['build_type'] = 'release'
        await self.send_message('Race info cleared!')

    async def update_info(self):
        if (self.state['seed_rolled']):
            await self.set_raceinfo('Randomizer {} Seed: {} Flags: {}'.format(
                self.state['race_version'], 
                self.state['race_seed'],
                self.state['race_flagstring']),
                overwrite=True)
            await self.send_message('Randomizer {} Seed: {} Flags: {}'.format(
                self.state['race_version'], 
                self.state['race_seed'],
                self.state['race_flagstring']))
            await self.print_url()

    async def print_url(self):
        build_type=self.state['build_type']
        if (self.state['seed_rolled'] and build_type='juef'):
            await self.send_message('https://snestop.jerther.com/misc/dwr/unofficial_juef/current/#flags={}&seed={}'.format(
                self.state['race_flagstring'], 
                self.state['race_seed']))
            return
        if (self.state['seed_rolled'] and (self.state['race_version'].startswith('v3.0') or self.state['race_version'].startswith('v2025-TE'))):
            await self.send_message('https://dwrandomizer.com/{}/#flags={}&seed={}'.format(
                build_type,
                self.state['race_flagstring'], 
                self.state['race_seed']))

    def _race_in_progress(self):
        return self.data.get('status').get('value') in ('pending', 'in_progress')
