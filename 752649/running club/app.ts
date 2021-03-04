import * as fs from 'fs';
import * as http from 'http';

import * as cheerio from 'cheerio';

let fileName = 'data.txt';
let outputName = 'output.csv';

fs.readFile(fileName, (err, contents) => {
    fs.writeFile(outputName, 'number,name,event,position,time,pb\n', (err) => {
        if (err) console.error(err);
    });

    if (err) {
        console.error('File could not be read');
        return;
    }

    let numbers = contents.toString().split(/\r?\n/).filter(string => string.trim().length > 0);

    for (let i in numbers) {
        let number = numbers[i];
        let content = "";
        let p = '/results/athleteresultshistory/?athleteNumber=' + number;
        http.get({
            host: 'www.parkrun.org.uk',
            port: 80,
            path: p
        }, (res) => {
            res.setEncoding("utf8");
            res.on("data", function (chunk) {
                content += chunk;
            });

            res.on("end", function () {
                let $ = cheerio.load(content);
                let name = $('h2').text().split('(')[0].trim();

                let firstRow = $('tbody tr')[0];
                let eventName = firstRow.children[0].children[1].children[0].data;
                let date = firstRow.children[1].children[0].data;
                let position = firstRow.children[3].children[0].data;
                let time = firstRow.children[4].children[0].data;

                let dateParts = date.split("/");
                let eventDate = new Date(Number(dateParts[2]), Number(dateParts[1]) - 1, Number(dateParts[0]));
                let compareDate = new Date();
                compareDate.setDate(compareDate.getDate() - 7);

                if (compareDate < eventDate) {
                    let urlEvent = '/' + eventName.split('parkrun')[0].trim().toLowerCase().replace(/\s/g, '') + '/results/athletehistory/?athleteNumber=' + number;
                    http.get({
                        host: 'www.parkrun.org.uk',
                        port: 80,
                        path: urlEvent
                    }, (res) => {
                        content = "";
                        res.setEncoding("utf8");
                        res.on("data", function (chunk) {
                            content += chunk;
                        });

                        res.on("end", function() {
                            $ = cheerio.load(content);

                            let pb = cheerio.load($('.sortable')[1])('tr')[1].children[5].children[0].data.trim();
                            
                            console.log(name + " got a " + position + "th place on the " + eventName + " event that occurred on " + date + " with a time of " + time + (pb == 'PB'?' (PB)':''));
                            fs.appendFile(outputName, number + ',' + name + ',' + eventName + ',' + position + ',' + time + ',' + (pb == 'PB'?'yes':'no') + '\n', (err) => {
                                if (err) console.error(err);
                            });
                        });
                    });
                } else {
                    fs.appendFile(outputName,number + ',' + name + ',,,,\n', (err) => {
                        if (err) console.error(err);
                    });
                }
            });
        });
    }
});