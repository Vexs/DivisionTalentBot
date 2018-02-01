import discord
from discord.ext import commands
import json
import re

class TalentLookup:
    """"""
    def __init__(self, bot):
        self.bot = bot
        with open("talents.json", "r") as f:
            self.talent_dict = json.load(f)

    @commands.command()
    async def talent(self, *,arg):
        """Looks up a talent!"""
        arg = arg.lower()
        talent = self.talent_dict.get(arg.lower())

        if not talent:
            possibles = finder(arg, self.talent_dict.keys(), lazy=False)
            if len(possibles) == 1:
                talent = self.talent_dict.get(possibles[0])
                arg = possibles[0]
            elif possibles:
                possibles = [x.title() for x in possibles]
                await self.bot.say("Did you mean...\n{}".format("\n".join(possibles[:5])))
                return
            else:
                await self.bot.say("No results found!")
                return

        embed = discord.Embed()
        embed.color=discord.Color(value=0xFF6D10)
        embed.set_author(name=arg.title())
        formatted_output = "{0}\n\n**Avaliable on/as:**\n{1}".format(*talent)
        embed.description = formatted_output

        await self.bot.say(embed=embed)

    @talent.error
    async def _talent_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            print(error)

def setup(bot):
    bot.add_cog(TalentLookup(bot))


def finder(text, collection, *, key=None, lazy=True):
    #Thanks to Rapptz
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]
