const cp = require('child_process')
const username = require('username').sync()
const socketio = require('socket.io')
const ProgressBar = require('progress')

exports.lifeslice = {
    builder: {
        input: {
            alias: 'i',
            default: `/Users/${username}/Library/Application Support/LifeSlice/webcam`
        },
        output: {
            alias: 'o',
            default: `/Users/${username}/Desktop/chronist-photos-${username}.csv`
        },
        debug: {
            alias: 'd',
            default: false
        }
    },
    handler
}

exports.photos = {
    builder: {
        input: {
            alias: 'i',
            required: true
        },
        output: {
            alias: 'o',
            required: true
        },
        debug: {
            alias: 'd',
            type: 'boolean',
            default: false
        }
    },
    handler
}

function handler(argv) {

    const env = Object.assign({}, process.env, argv)

    const analyzer = cp.spawn(`${__dirname}/../../node_modules/electron/cli.js`, [`${__dirname}/main.js`], { env })

    if (argv.debug) {
        console.log('Debug mode is enabled.')
    }

    console.log('Analyzing your photos...')

    analyzer.stdout.on('data', data => {
        let message = data.toString().trim()
        console.log(message)
    })

    analyzer.stderr.on('data', data => {
        let message = data.toString().trim()
        if (/^\[warn\]/.test(message)) {
            return
        }
        console.error(data.toString().trim())
        console.error('Could not complete analysis.')
        process.exit()
    })

    analyzer.on('close', (code) => {
      console.log(`child process exited with code ${code}`)
      process.exit()
    })

    const io = socketio().listen(6262)
    let bar = null

    io.on('connect', socket => {
        socket.on('update', status => {
            if (bar === null) {
                bar = new ProgressBar(':bar :current/:total (:percent)', {
                    total: status.total,
                    complete: '=',
                    incomplete: '-',
                })
            }
            bar.tick(status.complete - bar.curr)
        })
        socket.on('complete', _ => {
            process.exit()
        })
    })

}
