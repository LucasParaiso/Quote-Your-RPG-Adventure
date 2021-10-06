import Discord, { Intents, MessageEmbed } from 'discord.js'
import { join, dirname } from 'path'
import { Low, JSONFile } from 'lowdb'
import { fileURLToPath } from 'url'

import dotenv from 'dotenv'
dotenv.config()

const prefix = 'quote'
const __dirname = dirname(fileURLToPath(import.meta.url));
const file = join(__dirname, 'db.json')
const adapter = new JSONFile(file)
const db = new Low(adapter)

await db.read()

const client = new Discord.Client({
    intents: [
        Intents.FLAGS.GUILDS,
        Intents.FLAGS.GUILD_MESSAGES,
    ]
})

client.on('ready', () => {
    console.log('Pronto!')
})

client.on('messageCreate', (message) => {
    if (message.author.bot) return;
  
    const args = message.content.split(/ +/);
    const prefixo = args.shift();
    if (prefixo != prefix) return;
    const commandName = args.shift().toLowerCase();

    if (parseInt(commandName)) return message.reply({ 
        embeds: [enviaMensagem(commandName)] 
    });

    if (commandName === 'sort' || commandName === 's') {
        const itens = db.data.quotes.length
        const id = Math.floor(Math.random() * itens) + 1

        return message.reply({ 
            embeds: [enviaMensagem(id)] 
        })
    } else if (commandName === 'add') {
        const mensagem = `\n**Quote #${db.data.quotes.length + 1}**\n\n` + message.content.slice(10)

        db.data.quotes.push(mensagem)
        db.write()
        return message.reply({ 
            embeds: [enviaMensagem(db.data.quotes.length)] 
        });
    } else if (commandName === 'download') {
        message.channel.send({ files: ["./db.json"]});
    } else if (commandName === 'link') {
        return message.reply({
            content: "https://discord.com/oauth2/authorize?client_id=807816311463346186&scope=bot"
        })
    } else if (commandName === 'list') {
        const acessoDM = client.users.cache.get(message.author.id);
        acessoDM.send('Lista de Quotes')
        
        let jaEnviados = 0
        do {
            let enviar = []

            for (let i = jaEnviados; i < jaEnviados + 10; i++) {
                if (db.data.quotes[i] != undefined) {
                    enviar += '\n\n--------------------\n'
                    enviar += db.data.quotes[i]
                }
            }
            acessoDM.send(enviar)
            jaEnviados += 10

        } while(jaEnviados <= db.data.quotes.length)

        return message.reply("Quotes enviados na sua DM");
    }    

    function enviaMensagem(ID) {
        const embed = new MessageEmbed()
          .setColor("#f5ff00")
          .setAuthor(
            "QuoteBot",
            "https://i.pinimg.com/564x/2c/90/0e/2c900ee9719596d6a88b4c84bc900a97.jpg"
          )
          .setDescription(db.data.quotes[ID - 1]);
    
        return embed;
      }
})

client.login(process.env.TOKEN)
