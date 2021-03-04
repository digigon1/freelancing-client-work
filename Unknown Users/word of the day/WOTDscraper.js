var fs = require("fs");
var request = require("request-promise");
var cheerio = require("cheerio");
var sleep = require("thread-sleep");
var open = require("open");

var location = "./output/"; //FOLDER
var maxPages = 300;
var output = true; //EXTRA OUTPUT
var justOne = false; //GET JUST ONE PAGE
var choice = 0; //IF justOne IS SET, GET THIS PAGE

var done = false;

if (typeof Promise.prototype.done !== 'function') {
  Promise.prototype.done = function (onFulfilled, onRejected) {
    var self = arguments.length ? this.then.apply(this, arguments) : this
    self.then(null, function (err) {
      setTimeout(function () {
        throw err
      }, 0)
    })
  }
}

function main(){
	if(justOne){
		setTimeout(getOne, 300, choice);
	} else {
		setTimeout(getOne, 300, 0);
	}
}

function getOne(i){
  if(output)
    console.log("getting "+i);

  var propertiesObject = {
      q:"",
      sort:"newest",
      page:i,
      dom:"www.nytimes.com",
      dedupe_hl:"y",
      timeout:60000
    };
  
    var url = "https://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/column/learning-word-of-the-day";
    
    var json = null;

    var cont = getTopUrl(url, propertiesObject).then(result => {      

      var promises = [];
  
      for (var j = 0; j < result.length; j++) {
        promises.push(getUniqueUrl(result[j].url, 0));
      }
    
      Promise.all(promises).then(a => {
        if(output)
          console.log("promises end "+i);
        if(a.length != 0)
          fs.writeFile(location+"output"+i+".json",JSON.stringify(a, null, 4));
        else {
          console.log("done");
          done = true;
        }
      });
    }).done(() => {
      if(i < maxPages-1 && !done && !justOne){
        setTimeout(getOne, 5000, i+1);
      }
    });
}


function getTopUrl(url, propertiesObject){
  return request({url:url, qs:propertiesObject}).then(function(body, resp, err){
    if(err){
      console.log(err);
      return;
    }

    var items = JSON.parse(body).members.items;

    return items;
  }, function(reason){
    console.log("REASON: "+reason);
    return [];
  });
}

function getUniqueUrl(url, attempt){
  return request({url:url, jar:true, timeout:60000}).then(function(body, resp, err){
        var item = {};

        if(err){
          console.log("ERROR: "+err); 
          return item;
        }

        var $ = cheerio.load(body);

        // WORD

        var title = "";
        var pos = [];
        var fullTitle = $('strong',$('.story-subheading'));
        if(fullTitle == null || fullTitle.length == 0){
          fullTitle = $($('.story-subheading'),'.story-body');
          if(fullTitle == null || fullTitle.length == 0){
            fullTitle = $('strong',$('.story-body'));

            if(fullTitle == null || fullTitle.length == 0){
              fullTitle = $(".wod");

              if(fullTitle == null || fullTitle.length == 0){
                fullTitle = $('strong',$('p.story-body-text'));

                if(fullTitle == null || fullTitle.length == 0){
                  if(attempt < 10)
                    return getUniqueUrl(url, attempt+1);
                  else
                    return item;
                } else {
                  pos = fullTitle[0].children[0];
                }
              } else if(fullTitle[0].children.length > 1){
                pos = fullTitle[0].children[fullTitle[0].children.length-1].children[0].children[0];
              } else {
                pos = fullTitle[0].children[0];
              }
            } else {
              pos = fullTitle[0].children[0];
            }
          } else {
            pos = fullTitle[0].children[0];
          }
        } else {
          pos = fullTitle[0].children[0];
        }

        title = pos.data.replace(/([a-zA-Z\u00C0-\u017F]+)(.*)/,"$1");
        if(output)
          console.log(title);
        item.title = title;
        

        // EXAMPLE
        
        var divs = $('.story-body').children();
        if(divs == undefined || divs.length == 0){
          divs = $('.entry-content').children();
          if(divs == undefined || divs.length == 0){
            console.log("content");
            return item;
          }
        }
        var chosen = [];
        for (var i = 1; i < divs.length; i++) {
          var text = $(divs[i]).html().toLowerCase();
          text = $('<div/>').html(text).text();
          //var regex = new RegExp("^.*[^A-Za-z0-9_]+"+title+"[^A-Za-z0-9_]+.*$");
          if(text.includes(title) && !text.includes("The word <strong>")){
            chosen.push($(divs[i]).html());
          }
        }

        divs = [];
        for (var i = 0; i < chosen.length; i++) {
          var spl = chosen[i].split("\n");
          for (var j = 0; j < spl.length; j++) {
            var text = spl[j].toLowerCase();
            //console.log($('<div/>').html(text).text());
            //text = $('<div/>').html(text).text();
            if(text.includes("<strong>"+title+"</strong>"))
              divs.push(spl[j]);
          }
        }

        divs = divs.filter(s => {
          return !s.includes("Think you know") && !s.includes("New York Times article");
        });

        divs = divs.map(s => {
          var text = s.replace(/<strong>/g,"").replace(/<\/strong>/g,"").replace(/^<[^>]+>([^<]*)(<[^>]*>)?$/,"$1");
          return $('<div/>').html(text).text();
        })

        item.example = divs[0]; 
        /**/


        // DEFINITION
        
        var definition = [];

        var childList = $('.story-body').children();
        if(childList == undefined || childList.length == 0){
          childList = $('.entry-content').children();
          if(childList == undefined || childList.length == 0){
            console.log("content");
            return item;
          }
        }
        var reduced = [];
        for (var i = 1; i < childList.length; i++) {
          if($(childList[i]).html().includes("youtube"))
            continue;
          if($(childList[i]).html().replace(/<p>(<em>)?_*(<\/em>)?<\/p>/,"").includes("___"))
            break;
          reduced.push(childList[i]);
        }

        if(typeof reduced[0] == "undefined"){
          console.log("reduced "+childList.length);
          return item;
        }

        reduced = (reduced[0].name == "blockquote")?reduced[0].children:reduced;

        for (var i = 0; i < reduced.length; i++) {
          if(reduced[i].type == "text")
            continue;
          else {
            definition.push(clearStrong(reduced[i].children));
          }
        }

        item.definition = clearDef(definition);
        /**/


        //RETURN
        return item;
      },() => {
        if(attempt < 10)
            return getUniqueUrl(url, attempt+1);
          else
            return {};
      });
}

function clearDef(def){
  var result = [];
  for (var i = 0; i < def.length; i++) {
    if(new RegExp(/^\d+\./).test(def[i]) || new RegExp(/^(\w+)?:/).test(def[i]) || new RegExp(/\s\d+\./).test(def[i])){
      var defs = def[i].split("\n");
      for (var j = 0; j < defs.length; j++) {
        if(defs[j] !== "" && (defs[j].slice(-4) == "etc." || defs[j].slice(-1) !== ".") && new RegExp(/^(\d|(\w+)?:)/).test(defs[j]))
          result.push(defs[j]);
      }
    }
  }
  return result;
}

function clearStrong(children){
  var result = "";
  for (var i = 0; i < children.length; i++) {
    if(children[i].type == "text")
      result += children[i].data;
    else {
      if(children[i].children.length != 0)
        result += children[i].children[0].data;
    }
  }
  return result;
}

main();