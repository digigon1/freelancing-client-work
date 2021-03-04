import com.google.gson.*;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriBuilder;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.util.ArrayList;

/**
 * Created by digigon1 on 05/07/2017.
 */
public class Main {
    public static void main(String[] args) {
        Client client = ClientBuilder.newBuilder()
                .build();
        URI baseURI = UriBuilder.fromUri("https://gamepass.nfl.com/").build();
        WebTarget target = client.target( baseURI );

        JsonParser parser = new JsonParser();

        ArrayList<String> commands = new ArrayList<>();
        for (int season = 2011; season < 2017; season++) {
            commands.add("Season "+season+":");
            commands.add("");
            for (int type = 1; type < 4; type++) {
                int version = -1;
                for (int week = 0; week < 30; week++) {
                    System.out.println("Season "+season+", Type "+type+", Week "+week);
                    JsonObject json = parser.parse(target.path("/schedule")
                            .queryParam("season", season)
                            .queryParam("gametype", type)
                            .queryParam("week", week)
                            .queryParam("format", "json")
                            .request()
                            .get(String.class)).getAsJsonObject();

                    JsonArray games = json.getAsJsonArray("games");
                    if(games == null){
                        System.err.println("Could not get games json, is the network properly connected?");
                        System.exit(1);
                    }
                    for (int i = 0; i < games.size(); i++) {
                        JsonObject game = games.get(i).getAsJsonObject();
                        String fullName = game.get("seoName").getAsString();
                        String fullDate = game.get("date").getAsString();
                        String[] date = fullDate.split("T")[0].split("-");
                        String statsId = game.get("statsId").getAsString();
                        String extID = game.get("extId").getAsString();
                        JsonObject homeTeam = game.get("homeTeam").getAsJsonObject();
                        String homeCode = homeTeam.get("code").getAsString().toLowerCase();
                        String homeName = homeTeam.get("name").getAsString();
                        JsonObject awayTeam = game.get("awayTeam").getAsJsonObject();
                        String awayCode = awayTeam.get("code").getAsString().toLowerCase();
                        String awayName = awayTeam.get("name").getAsString();
                        ArrayList<String> links = new ArrayList<>();
                        links.add(String.format("https://nlds53.cdnllnwnl.neulion.com/mobile/nfl/vod/%s/%s/%s/%s/ipad/%d_%s_%s_%s_%d_h_whole/v1/playlist.m3u8", date[0], date[1], date[2], statsId, type, statsId, awayCode, homeCode, season));
                        links.add(String.format("https://nlds53.cdnllnwnl.neulion.com/mobile/nfl/vod/%s/%s/%s/%s/ipad/%d_%s_%s_%s_%d_h_whole/v2/playlist.m3u8", date[0], date[1], date[2], extID, type, extID, awayCode, homeCode, season));
                        links.add(String.format("https://nlds53.cdnllnwnl.neulion.com/mobile/nfl/vod/%s/%s/%s/%s/ipad/%d_%s_%s_%s_%d_h_whole/v3/playlist.m3u8", date[0], date[1], date[2], statsId, type, statsId, awayCode, homeCode, season));
                        links.add(String.format("https://nlds53.cdnllnwnl.neulion.com/mobile/nfl/vod/%s/%s/%s/%s/ipad/%d_%s_%s_%s_%d_h_whole/v4/playlist.m3u8", date[0], date[1], date[2], statsId, type, statsId, awayCode, homeCode, season));
                        for (int j = 1; j < 10; j++) {
                            links.add(String.format("https://nlds82.cdnllnwnl.neulion.com/nlds_vod/nfl3/vod/%s/%s/%s/%s/%d_%s_%s_%s_%s_h_whole_%d_ipad.mp4.m3u8%s", date[0], date[1], date[2], statsId, type, statsId, awayCode, homeCode, season, j, "?h=603dd9807a540b89b00281e0ab22e3d5.1499127524&hdnea=exp=1499156264~acl=/nlds_vod/nfl3/vod/2016/09/25/56935/4512d8/*~hmac=B438703279DDE80ADA60143C89E3EAF96C2BDC930E94316A39B8FBD47E615D5F&nltid=nflgp&nltdt=0&uid=2037651"));
                        }

                        Client testClient = ClientBuilder.newBuilder().build();
                        if(version >= 0) {
                            String l = links.get(version);
                            URI uri = UriBuilder.fromUri(l).build();
                            WebTarget t = testClient.target(uri);
                            Response r = t.request().get();
                            if (r.getStatus() == 200) {
                                String[] lines = r.readEntity(String.class).split("\n");

                                int dot;
                                int max = 0;
                                String link;
                                if(version < 4) {
                                    for (int k = 1; k < lines.length; k++) {
                                        max = Math.max(max, Integer.parseInt(lines[k].substring(lines[k].lastIndexOf("=") + 1).trim()) / 1000);
                                        k++;
                                    }
                                    dot = l.lastIndexOf(".");
                                    link = l.substring(0, dot) + "_" + max + l.substring(dot);
                                } else {
                                    for (int k = 1; k < lines.length; k++) {
                                        max = Math.max(max, Integer.parseInt(lines[k].substring(lines[k].indexOf("BANDWIDTH=") + "BANDWIDTH=".length()).split(",")[0]) / 1000);
                                        k++;
                                    }
                                    link = l;
                                }
                                commands.add(String.format("streamlink %s -o \"%s @ %s on %s.ts\" \"%s://%s\" best", getCookies(season), awayName, homeName, fullDate.split("T")[0], season>=2013?"hls":"hlsvariant", link));
                                continue;
                            }
                        }

                        int j = 0;
                        for(String l : links){
                            URI uri = UriBuilder.fromUri(l).build();
                            WebTarget t = testClient.target( uri );
                            Response r = t.request().get();
                            if(r.getStatus() == 200){
                                version = j;
                                String[] lines = r.readEntity(String.class).split("\n");

                                int dot;
                                int max = 0;
                                String link;
                                if(j < 4) {
                                    for (int k = 1; k < lines.length; k++) {
                                        max = Math.max(max, Integer.parseInt(lines[k].substring(lines[k].lastIndexOf("=") + 1).trim()) / 1000);
                                        k++;
                                    }
                                    dot = l.lastIndexOf(".");
                                    link = l.substring(0, dot) + "_" + max + l.substring(dot);
                                } else {
                                    for (int k = 1; k < lines.length; k++) {
                                        max = Math.max(max, Integer.parseInt(lines[k].substring(lines[k].indexOf("BANDWIDTH=") + "BANDWIDTH=".length()).split(",")[0]) / 1000);
                                        k++;
                                    }
                                    link = l;
                                }
                                commands.add(String.format("streamlink %s -o \"%s @ %s on %s.ts\" \"%s://%s\" best", getCookies(season), awayName, homeName, fullDate.split("T")[0], season>=2013?"hls":"hlsvariant", link));
                                break;
                            }
                            j++;
                        }
                        if(j == links.size()){
                            System.out.println(String.format("Failed at: %s @ %s", fullName, fullDate));
                        }
                    }
                }
            }

            try(PrintWriter writer = new PrintWriter("Season_"+season+".txt", "UTF-8")){
                for (String cmd : commands)
                    writer.println(cmd);
            } catch (FileNotFoundException | UnsupportedEncodingException e) {
                e.printStackTrace();
            } finally {
                commands.clear();
            }
        }


    }

    private static String getCookies(int season) {
        if(season > 2012)
            return "--http-header \"User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0\" --http-cookie \"X-NL-SK-nlds_vod-nfl3-vod-2016-09-08-56901=d84a0883dbe271761194bc45437dbc4b.1499447347098; X-NL-SK-nlds_vod-nfl3-vod-2016-09-11-56908=6e37e908817a55d693745040879a7c18.1499447357850; X-NL-SK-nlds_vod-nfl3-vod-2016-09-11-56907=154f9a9879a3a6cd251f8021c98ae9d2.1499447176052\"";
        else
            return "";
    }
}
