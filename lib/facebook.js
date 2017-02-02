const fs = require('fs')
const path = require('path')
const moment = require('moment')
const username = require('username').sync()
const CSV = require('big-csv')

const getSentimentScores = require('./get-sentiment-scores')

exports.builder = {
    input: {
        alias: 'i',
        required: 'Please specify the path to your messages.htm'
    },
    output: {
        alias: 'o',
        default: `/Users/${username}/Desktop/chronist-facebook-${username}.csv`
    },
    name: {
        alias: 'n',
        required: 'Please specify your name as it appears on Facebook by running this command with `-n "Your Name"`'
    },
    nopython: {
        default: false
    }
}

exports.handler = argv => {

    if (!fs.existsSync(argv.input)) {
        console.error(`File ${argv.input} does not exist`)
        return
    }

    if (argv.nopython) {
        nopythonHandler(argv)
    } else {
        handler(argv)
    }

}

function nopythonHandler(argv) {

    const jsdom = require('jsdom')

    const inputFilePath = path.resolve(argv.input)
    const outputFilePath = path.resolve(argv.output)
    const csv = new CSV(outputFilePath, { flags: 'w+' })

    jsdom.env(inputFilePath, (error, window) => {
        if (error) throw error
        let messages = []
        Array(...window.document.querySelectorAll('.message')).forEach(m => {
            let user = m.querySelector('.user').textContent
            if (user !== argv.name) {
                return
            }
            let scores = getSentimentScores(m.nextSibling.textContent)
            let dateText = m.querySelector('.meta').textContent.match(/([a-zA-Z]+ \d+, \d{4}) at (\d+:\d+(am|pm))/)
            let date = moment(`${dateText[1]} ${dateText[2]}`, 'MMMM D, YYYY HH:mm')
            scores.date = date.format('YYYY-MM-DD')
            scores.time = date.format('HH:mm:ss')
            csv.write(scores)
            return scores
        })
        console.log(`Saved results to ${argv.output}`)
    })
}

function handler(argv) {

    const cp = require('child_process')

    const outputFilePath = path.resolve(argv.output)
    const csv = new CSV(outputFilePath, { flags: 'w+' })

    cp.execSync(`pip install -r ${__dirname}/../requirements.txt`, { env: process.env })

    let env = Object.assign({
        NAME: argv.name,
        INPUT_FILE: argv.input
    }, process.env)

    let py = cp.spawn('python', [`${__dirname}/facebook.py`], { env })

    let json = ''

    py.stdout.on('data', data => {
        json += data.toString()
    })

    py.stderr.on('data', error => {
        throw new Error(error)
    })

    py.on('close', code => {
        JSON.parse(json).map(message => {
            if (!message.text) {
                return
            }
            let dateText = message.date.match(/([a-zA-Z]+ \d+, \d{4}) at (\d+:\d+(am|pm))/)
            if (!dateText) {
                return
            }
            let scores = getSentimentScores(message.text)
            let date = moment(`${dateText[1]} ${dateText[2]}`, 'MMMM D, YYYY HH:mm')
            scores.date = date.format('YYYY-MM-DD')
            scores.time = date.format('HH:mm:ss')
            csv.write(scores)
            return scores
        })
        console.log(`Saved results to ${argv.output}`)
    })
}
