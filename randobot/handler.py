from racetime_bot import RaceHandler, monitor_cmd, can_moderate, can_monitor
import random

class RandoHandler(RaceHandler):
    """
    RandoBot race handler. Generates seeds, presets, and frustration.
    """
    stop_at = ['cancelled', 'finished']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seed_rolled = False

    def should_stop(self):
        return (
           # (
           #     self.data.get('goal', {}).get('name') == 'Random settings league'
           #     and not self.data.get('goal', {}).get('custom', False)
           # )
           # or
           super().should_stop()
        )

    async def begin(self):
        """
        Send introduction messages.
        """
        if self.should_stop():
            return
        if not self.state.get('intro_sent') and not self._race_in_progress():
            await self.send_message(
                'Welcome to DWR! Create a seed with !dwflags <flags>'
            )
            self.state['intro_sent'] = True
        if 'locked' not in self.state:
            self.state['locked'] = False
        if 'fpa' not in self.state:
            self.state['fpa'] = False

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

    @monitor_cmd
    async def ex_dwflags(self, args, message):
        """
        Handle !dwflags commands.
        """
        if self._race_in_progress():
            return
        await self.roll_and_send(args, message)

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

        await self.roll(
            flags=args[0] if args else 'weekly',
            reply_to=reply_to,
        )

    async def roll(self, flags, reply_to):
        """
        Roll a new seed and update the race info.
        """
        await self.set_raceinfo('Randomizer v2.2.1 Seed {seed} Flags {flagstring}'.format(
            seed=random.randint(1000000000000, 10000000000000),
            flagstring=flags
        )

        await self.send_message('GLHF!')

    def _race_in_progress(self):
        return self.data.get('status').get('value') in ('pending', 'in_progress')
