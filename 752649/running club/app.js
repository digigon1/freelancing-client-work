"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var fs = require("fs");
var http = require("http");
var cheerio = require("cheerio");
var fileName = 'data.txt';
var outputName = 'output.csv';
fs.readFile(fileName, function (err, contents) {
    fs.writeFile(outputName, 'number,name,event,position,time,pb\n', function (err) {
        if (err)
            console.error(err);
    });
    if (err) {
        console.error('File could not be read');
        return;
    }
    var numbers = contents.toString().split(/\r?\n/).filter(function (string) { return string.trim().length > 0; });
    var _loop_1 = function (i) {
        var number = numbers[i];
        var content = "";
        var p = '/results/athleteresultshistory/?athleteNumber=' + number;
        http.get({
            host: 'www.parkrun.org.uk',
            port: 80,
            path: p
        }, function (res) {
            res.setEncoding("utf8");
            res.on("data", function (chunk) {
                content += chunk;
            });
            res.on("end", function () {
                var $ = cheerio.load(content);
                var name = $('h2').text().split('(')[0].trim();
                var firstRow = $('tbody tr')[0];
                var eventName = firstRow.children[0].children[1].children[0].data;
                var date = firstRow.children[1].children[0].data;
                var position = firstRow.children[3].children[0].data;
                var time = firstRow.children[4].children[0].data;
                var dateParts = date.split("/");
                var eventDate = new Date(Number(dateParts[2]), Number(dateParts[1]) - 1, Number(dateParts[0]));
                var compareDate = new Date();
                compareDate.setDate(compareDate.getDate() - 7);
                if (compareDate < eventDate) {
                    var urlEvent = '/' + eventName.split('parkrun')[0].trim().toLowerCase().replace(/\s/g, '') + '/results/athletehistory/?athleteNumber=' + number;
                    http.get({
                        host: 'www.parkrun.org.uk',
                        port: 80,
                        path: urlEvent
                    }, function (res) {
                        content = "";
                        res.setEncoding("utf8");
                        res.on("data", function (chunk) {
                            content += chunk;
                        });
                        res.on("end", function () {
                            $ = cheerio.load(content);
                            var pb = cheerio.load($('.sortable')[1])('tr')[1].children[5].children[0].data.trim();
                            console.log(name + " got a " + position + "th place on the " + eventName + " event that occurred on " + date + " with a time of " + time + (pb == 'PB' ? ' (PB)' : ''));
                            fs.appendFile(outputName, number + ',' + name + ',' + eventName + ',' + position + ',' + time + ',' + (pb == 'PB' ? 'yes' : 'no') + '\n', function (err) {
                                if (err)
                                    console.error(err);
                            });
                        });
                    });
                }
                else {
                    fs.appendFile(outputName, number + ',' + name + ',,,,\n', function (err) {
                        if (err)
                            console.error(err);
                    });
                }
            });
        });
    };
    for (var i in numbers) {
        _loop_1(i);
    }
});
//# sourceMappingURL=app.js.map