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
                    'Welcome to DWR! Create a standard seed with !roll'
                )
            else:
                await self.send_message(
                    'Welcome to DWR! Create a custom flag seed with !dwflags <flags>'
                )
            await self.send_message(
                'Full list of raceroom commands at https://pastebin.com/raw/4nKVRxXR'
            )
            self.state['intro_sent'] = True
        if 'locked' not in self.state:
            self.state['locked'] = False

        self.state['seed_rolled'] = False

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
        """
        Handle !dwflags commands.
        """
        if self._race_in_progress():
            return
        if not self.state['race_version']:
            self.state['race_version'] = 'v2.2.1'
        await self.roll_and_send(args, message)

    async def ex_dwflags3(self, args, message):
        """
        Handle !dwflags3 commands.
        """
        if self._race_in_progress():
            return
        if not self.state['race_version']:
            self.state['race_version'] = 'v3.0'
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

    async def ex_url(self, args, message):
        await self.print_url()

    async def ex_clear(self, args, message):
        """
        Clears seed and flag from internal state and raceroom info.
        """
        await self.clear()

    async def ex_roll(self, args, message):
        """
        Rolls a new seed with the room default flags.
        """
        reply_to = message.get('user', {}).get('name')
        
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
            await self.roll(
                flags="CDFGMPRSTWZar",
                reply_to=reply_to,
            )
        else:
            await self.send_message('This command only works in Standard and Tournament')

    async def ex_roll3(self, args, message):
        """
        Rolls a new seed with the room default flags for version 3.0.
        """
        reply_to = message.get('user', {}).get('name')
        
        goal_name = self.data.get('goal', {}).get('name')
        if (goal_name == 'Standard Flags' or goal_name == 'Tournament'):
            self.state['race_version'] = 'v3.0'
            await self.roll(
                flags="IVIAAVCAKACAAAAAAAAAAEAA",
                reply_to=reply_to,
            )
        else:
            await self.send_message('This command only works in Standard and Tournament')


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
        if (self.state['seed_rolled']):
            await self.send_message('https://dwrandomizer.com/release/#flags={}}&seed={}}'.format(
                self.state['race_flagstring'], 
                self.state['race_seed']))

    def _race_in_progress(self):
        return self.data.get('status').get('value') in ('pending', 'in_progress')
