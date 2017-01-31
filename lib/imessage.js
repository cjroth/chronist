const fs = require('fs')
const path = require('path')
const iMessage = require('imessage')
const username = require('username')
const moment = require('moment')
const CSV = require('big-csv')

const getSentimentScores = require('./get-sentiment-scores')

exports.builder = {
    output: {
        default: `/Users/${username.sync()}/Desktop/chronist-imessage-${username.sync()}.csv`
    }
}

exports.handler = argv => {

    const outputFilePath = path.resolve(argv.output)
    const csv = new CSV(outputFilePath, { flags: 'w+' })

    const im = new iMessage()

    im.getMessages((error, messages) => {
        if (error) throw error
        messages
            .filter(m => m.is_from_me)
            .map(m => {
                let scores = getSentimentScores(m.text)
                let date = moment(m.date * 1000).add(31, 'years')
                scores.date = date.format('YYYY-MM-DD')
                scores.time = date.format('HH:mm:ss')
                csv.write(scores)
                return scores
            })
        console.log(`Saved results to ${argv.output}`)
    })

}
