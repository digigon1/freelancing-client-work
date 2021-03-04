drop table if exists livemar2_LiveFeed.news;



CREATE TABLE livemar2_LiveFeed.news (
  `updated` VARCHAR(30) NULL,
  `title` VARCHAR(200) NULL,
  `ticker` VARCHAR(16) NULL,
  `price` VARCHAR(16) NULL,
  `link` VARCHAR(200) not NULL,
  `form_title` varchar(200) null,
  `origin` varchar(200),
  `perc_change` varchar(50) null,
  PRIMARY KEY (link)
);

drop table if exists livemar2_LiveFeed.cik;

CREATE TABLE livemar2_LiveFeed.cik (
	cik varchar(20) primary key,
    ticker varchar(10)
);
