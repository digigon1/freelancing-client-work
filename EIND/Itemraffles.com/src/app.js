const https = require("https");
const http = require("http");
const fs = require("fs");

const bodyParser = require("body-parser");
const express = require("express");
const passport = require("passport");
const twitchStrat = require("passport-twitch").Strategy;
const TwitchBot = require('twitch-bot');

const app = express();

const bots = {};

app.use(express.static('static'));

passport.use(new twitchStrat({
    clientID: '<clientID>',
    clientSecret: '<clientSecret>',
    callbackURL: 'https://' + 'localhost:8443' + '/auth/twitch/callback',
    scope: 'channel_read'
}, function (accessToken, refreshToken, profile, done) {
    const bot = new TwitchBot({
        username: profile.username,
        oauth: 'oauth:' + accessToken
    });

    bot.on('join', function (channel) {
        console.log('Joined ' + channel)
    });

    bot.on('error', function (err) {
        console.log(err);
    });

    bot.on('message', function (chatter) {
        console.log(chatter);
    });

    bot.on('close', function() {
        console.log('closed bot irc connection');
    });

    bot.on('part', function() {
        console.log('bot parted');
    });

    bots[profile.username] = bot;

    bot.join(profile.username);

    done(null, null);
}));

app.get('/auth/twitch', passport.authenticate('twitch'));
app.get('/auth/twitch/callback', passport.authenticate('twitch', {failureRedirect: '/index.html'}), function (req, res) {
    res.redirect('index.html');
});


const privateKey = fs.readFileSync('localhost-key.pem', 'utf8');
const certificate = fs.readFileSync('localhost.pem', 'utf8');
const credentials = {
    key: privateKey,
    cert: certificate
};
https.createServer(credentials, app).listen(8443);

http.createServer(function (req, res) {
    console.log(req.headers['host']);
    let loc = "https://" + req.headers['host'].split(':')[0] + ':8443' + req.url;
    console.log(loc);
    res.writeHead(301, {
        "Location": loc
    });
    return res.end();
}).listen(8080);
