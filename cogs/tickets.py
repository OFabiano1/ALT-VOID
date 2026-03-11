import discord
from discord.ext import commands

AXOLOTE = "XD"

# ── Configure aqui ───────────────────────────────────────────
MOD_ROLE_ID = 994118849752481847
TICKET_CHANNEL_ID = 1148417761987534918
# ─────────────────────────────────────────────────────────────


class BotaoTicket(discord.ui.View):
    """View persistente com o botão de abrir ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📩 abrir ticket",
        style=discord.ButtonStyle.primary,
        custom_id="ticket:abrir",
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        autor = interaction.user

        for thread in guild.threads:
            if thread.name == f"ticket-{autor.name}" and not thread.archived:
                await interaction.response.send_message(
                    f"{AXOLOTE} você já tem um ticket aberto: {thread.mention}",
                    ephemeral=True,
                )
                return

        canal = guild.get_channel(TICKET_CHANNEL_ID)
        if canal is None:
            await interaction.response.send_message(
                "❌ canal de tickets não encontrado. avise um administrador!",
                ephemeral=True,
            )
            return

        thread = await canal.create_thread(
            name=f"ticket-{autor.name}",
            type=discord.ChannelType.private_thread,
            invitable=False,
            reason=f"Ticket aberto por {autor}",
        )

        await thread.add_user(autor)
        cargo_mod = guild.get_role(MOD_ROLE_ID)
        if cargo_mod:
            for membro in cargo_mod.members:
                await thread.add_user(membro)

        embed = discord.Embed(
            title="📩 Ticket Aberto",
            description=(
                f"olá {autor.mention}! {AXOLOTE}\n\n"
                "descreva seu problema ou dúvida aqui.\n"
                "um moderador irá te atender em breve!\n\n"
                "para fechar o ticket use `>fecharticket`."
            ),
            color=0xFF69B4,
        )
        embed.set_footer(text="ALT • Sistema de Tickets")

        view_fechar = FecharTicketView()
        await thread.send(embed=embed, view=view_fechar)

        await interaction.response.send_message(
            f"{AXOLOTE} ticket criado! {thread.mention}",
            ephemeral=True,
        )


class FecharTicketView(discord.ui.View):
    """Botão de fechar ticket dentro da thread."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 fechar Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="ticket:fechar",
    )
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _fechar_ticket(interaction.channel, interaction.user, interaction)


async def _fechar_ticket(thread: discord.Thread, autor: discord.Member, interaction=None):
    embed = discord.Embed(
        title="🔒 ticket fechado",
        description=f"fechado por {autor.mention}. {AXOLOTE}",
        color=0x888888,
    )
    if interaction:
        await interaction.response.send_message(embed=embed)
    else:
        await thread.send(embed=embed)

    await thread.edit(archived=True, locked=True)


class Tickets(commands.Cog, name="tickets"):
    """Sistema de tickets via thread privada."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(BotaoTicket())
        bot.add_view(FecharTicketView())

    # ── >setupticket ─────────────────────────────────────────
    @commands.command(name="setupticket")
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx: commands.Context):
        """[Admin] Envia o embed com o botão de abrir ticket no canal configurado."""
        canal = ctx.guild.get_channel(TICKET_CHANNEL_ID)
        if canal is None:
            await ctx.send("❌ canal de tickets não encontrado! verifique o `TICKET_CHANNEL_ID` na cog.")
            return

        embed = discord.Embed(
            title="Boas-vindas ao suporte!",
            description=(
                "Boas-vindas à sala de atendimento da comunidade.\n"
                "Por aqui você pode reportar bugs de bots, realizar uma denúncia de outros membros, "
                "pedir ajuda ou entrar em contato diretamente com a equipe de suporte para solicitar "
                "parcerias (sorteios, boost e patrocínios) e adicionar bots."
            ),
            color=0x121E,
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1017344173843693628/1334656061831122965/image.png?ex=69b1f0d1&is=69b09f51&hm=4cd4046585305d5e82b90d47c6ce35878e116e0fe4f0866fa4ff4e0f277eeba1&")
        embed.set_footer(text=(
            "- Não abra tickets somente para testar, pois isso pode atrapalhar o atendimento e tomar tempo da administração.\n"
            "- Seu ticket é aberto de forma anônima e somente os moderadores e suporte terão acesso às informações.\n\n"
            "© 2020 – 2026 Axoltol BR. Todos os direitos reservados.\n\n"
            " Para dar início ao seu atendimento, selecione uma das opções abaixo."
        ))

        await canal.send(embed=embed, view=BotaoTicket())
        await ctx.send(f"{AXOLOTE} embed de tickets enviado em {canal.mention}!", delete_after=5)

    # ── >fecharticket ────────────────────────────────────────
    @commands.command(name="fecharticket")
    async def fechar_ticket(self, ctx: commands.Context):
        """Fecha o ticket atual (dentro de uma thread de ticket)."""
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send(f"{AXOLOTE} este comando só funciona dentro de um ticket!")
            return
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send(f"{AXOLOTE} este não parece ser um canal de ticket!")
            return

        await _fechar_ticket(ctx.channel, ctx.author)

    # ── >addticket ───────────────────────────────────────────
    @commands.command(name="addticket")
    @commands.has_permissions(manage_threads=True)
    async def add_ticket(self, ctx: commands.Context, membro: discord.Member):
        """[Mod] Adiciona um membro ao ticket atual."""
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send(f"{AXOLOTE} use dentro de um ticket!")
            return
        await ctx.channel.add_user(membro)
        await ctx.send(f"{AXOLOTE} {membro.mention} adicionado ao ticket!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))