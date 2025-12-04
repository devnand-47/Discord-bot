# cogs/roles.py

import discord
from discord.ext import commands
from discord import app_commands

from config import ADMIN_ROLE_IDS


def is_admin():
    async def predicate(interaction: discord.Interaction):
        member = interaction.user
        if isinstance(member, discord.Member):
            if member.guild_permissions.administrator:
                return True
            if any(r.id in ADMIN_ROLE_IDS for r in member.roles):
                return True
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        raise app_commands.CheckFailure("Not admin")
    return app_commands.check(predicate)


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        super().__init__(label=role.name, style=discord.ButtonStyle.primary)
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if not isinstance(member, discord.Member):
            return
        if self.role in member.roles:
            await member.remove_roles(self.role, reason="Role menu remove")
            await interaction.response.send_message(
                f"❌ Removed {self.role.mention}", ephemeral=True
            )
        else:
            await member.add_roles(self.role, reason="Role menu add")
            await interaction.response.send_message(
                f"✅ Added {self.role.mention}", ephemeral=True
            )


class RoleMenuView(discord.ui.View):
    def __init__(self, roles: list[discord.Role]):
        super().__init__(timeout=None)
        for role in roles:
            self.add_item(RoleButton(role))


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rolemenu",
        description="Create a role menu with buttons.",
    )
    @is_admin()
    async def rolemenu(
        self,
        interaction: discord.Interaction,
        role1: discord.Role,
        role2: discord.Role | None = None,
        role3: discord.Role | None = None,
    ):
        roles = [r for r in (role1, role2, role3) if r is not None]
        if not roles:
            await interaction.response.send_message(
                "❌ No roles given.", ephemeral=True
            )
            return

        view = RoleMenuView(roles)
        await interaction.response.send_message(
            "Role menu created below:", ephemeral=True
        )
        await interaction.channel.send("Pick your roles:", view=view)  # type: ignore


async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))
