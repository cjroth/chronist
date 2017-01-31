const sentiment = require('sentiment')

module.exports = (message) => {
    let result = sentiment(message || '')
    return {
        sentiment: {
            score: result.score,
            comparative: result.comparative,
            positive_count: result.positive.length,
            negative_count: result.negative.length
        }
    }
}
