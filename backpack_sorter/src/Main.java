import com.github.koraktor.steamcondenser.steam.community.WebApi;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileWriter;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.text.SimpleDateFormat;
import java.util.*;

public class Main {

    public static void main(String[] args) {
        try {
            File f = new File("config.cfg");
            SimpleDateFormat date = new SimpleDateFormat("dd-MM-yy");
            String steamApiKey;
            String bptfApiKey;
            if(f.exists() && !f.isDirectory()){
                Scanner fileRead = new Scanner(f);
                JSONObject config = new JSONObject(fileRead.next());
                fileRead.close();
                steamApiKey = config.getString("steamApiKey");
                bptfApiKey = config.getString("bptfApiKey");
            } else {
                Scanner in = new Scanner(System.in);
                System.out.println("Steam API key:");
                steamApiKey = in.next();
                in.nextLine();
                System.out.println("BPTF API key:");
                bptfApiKey = in.next();
                in.close();
            }

            String steamId = null;
            boolean replace = false;
            if (args.length != 0) {
                steamId = args[0];
                replace = true;
            } else if (f.exists() && !f.isDirectory()) {
                Scanner fileRead = new Scanner(f);
                JSONObject config = new JSONObject(fileRead.next());
                fileRead.close();
                steamId = config.getString("id");
            } else {
                System.out.println("Usage: java -jar <JarFile> listType type1 type2 type3");
                System.out.println("listType is either f (for friends) or g (for group)");
                System.exit(0);
            }

            WebApi.setApiKey(steamApiKey);
            WebApi.setSecure(true);
            /*************************************/


            Map<String, Object> params = new TreeMap<>();
            params.put("language","en");
            JSONObject schema = new JSONObject(WebApi.getJSON("IEconItems_440","GetSchema", 1, params)).getJSONObject("result");
            //TODO schema into map and use map in print


            JSONObject names = schema.getJSONObject("qualityNames");
            JSONObject qualities = schema.getJSONObject("qualities");
            Map<Long, String> idToQual = new HashMap<>();
            for(int i = 0; i < names.names().length(); i++){
                String id = names.names().getString(i);
                idToQual.put(qualities.getLong(id), names.getString(id));
            }

            JSONArray items = schema.getJSONArray("items");
            Map<Long, Map<Long,String>> idToName = new HashMap<>();
            for (int i = 0; i < items.length(); i++) {
                JSONObject item = items.getJSONObject(i);
                if(!idToName.containsKey(item.getLong("defindex"))) {
                    Map<Long, String> map = new HashMap<>();
                    map.put(item.getLong("item_quality"), item.getString("item_name"));
                    idToName.put(item.getLong("defindex"), map);
                } else {
                    idToName.get(item.getLong("defindex")).put(item.getLong("item_quality"), item.getString("name"));
                }
            }

            params.put("SteamID", steamId);
            JSONObject response = new JSONObject(WebApi.getJSON("IEconItems_440","GetPlayerItems", 1, params)).getJSONObject("result");
            if(response.getInt("status") == 1){
                items = response.getJSONArray("items");
                Map<Long, Map<Long, String>> prices = new HashMap<>();
                for (int i = 0; i < items.length(); i++) {
                    try {
                        //System.out.println();
                        JSONObject item = items.getJSONObject(i);

                        try{
                            if(item.getBoolean("flag_cannot_trade"))
                                continue;
                        } catch(Exception e){}


                        //System.out.println(item.getString("name"));
                        long itemID = item.getLong("defindex");
                        long quality = item.getLong("quality");
                        StringBuilder name = new StringBuilder();
                        name.append(idToQual.get(quality));
                        name.append(' ');
                        name.append(idToName.get(itemID).getOrDefault(quality, idToName.get(itemID).get(idToName.get(itemID).keySet().iterator().next())));
                        if(!prices.containsKey(itemID) || !prices.get(itemID).containsKey(quality)) {
                            /*
                            URL itemUrl = new URL();
                            //price info

                            URLConnection conn = itemUrl.openConnection();
                            conn.setRequestProperty("User-Agent", "Test");
                            InputStream stream = conn.getInputStream();
                            Scanner s = new Scanner(stream);
                            */
                            //System.out.println(quality);
                            //System.out.println(idToQual.get(quality));
                            JSONObject itemObj = new JSONObject(getResponse("https://backpack.tf/api/IGetPriceHistory/v1?key=" + bptfApiKey + "&item=" + itemID + "&quality=" + idToQual.get(quality))).getJSONObject("response");
                            //s.close();
                            String price = "";
                            if (itemObj.getInt("success") == 1) {
                                JSONArray priceArray = itemObj.getJSONArray("history");
                                if (priceArray.length() != 0) {
                                    JSONObject pObj = priceArray.getJSONObject(priceArray.length() - 1);
                                    price = pObj.getDouble("value") + " " + pObj.getString("currency");
                                } else {
                                    System.err.println(name.toString());
                                    //price = "Error: price history came up empty";
                                    continue;
                                }
                            } else {
                                System.err.println(name.toString());
                                //price = "Error: failed to get price history";
                                continue;
                            }
                            Map<Long, String> n = prices.get(itemID);
                            if(n == null)
                                n = new HashMap<>();
                            n.put(quality, price);
                            prices.put(itemID, n);
                        }


                        System.out.println(name.toString()+": "+prices.get(itemID).get(quality));
                    } catch (Exception e){
                        e.printStackTrace();
                    }
                }

            }


            /******************************/
            if (replace) {
                FileWriter writeConfig = new FileWriter(f);
                JSONObject obj = new JSONObject();
                obj.put("steamApiKey", steamApiKey);
                obj.put("id", steamId);
                obj.put("bptfApiKey", bptfApiKey);
                writeConfig.write(obj.toString());
                writeConfig.close();
            }
        } catch (Exception e){
            e.printStackTrace();
        }
    }

    private static String getResponse(String url) throws Exception{
        String result = "";
        URL itemUrl = new URL(url);
        //TODO open connection and get info
        //price info
        String price = "";
        URLConnection conn = itemUrl.openConnection();
        conn.setRequestProperty("User-Agent", "Test");
        InputStream stream = conn.getInputStream();
        Scanner s = new Scanner(stream);
        result = s.next();
        s.close();
        return result;
    }
}
