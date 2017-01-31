const { app, BrowserWindow, dialog, ipcMain } = require('electron')
const path = require('path')
const io = require('socket.io-client')
const moment = require('moment')
const url = require('url')

const socket = io('http://localhost:6262')

console.log(`Input Photo Directory: ${process.env.input}`)
console.log(`Output CSV File: ${process.env.output}`)

var window

if (process.env.debug === 'false') {
    app.dock.hide()
}

app.on('ready', function() {
    window = new BrowserWindow({
        title: 'Emotion Analysis',
        show: process.env.debug === 'true',
        webPreferences: {
            experimentalFeatures: true
        }
    })
    window.loadURL(url.format({
        pathname: path.join(__dirname, 'analyzer.html'),
        protocol: 'file:',
        slashes: true
    }))
    window.webContents.openDevTools()
})

ipcMain.on('update', (event, status) => {
    socket.emit('update', status)
})

ipcMain.on('complete', event => {
    socket.emit('complete')
    window.close()
})

ipcMain.on('error', (window, error) => {
    console.error(error)
})
