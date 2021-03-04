import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class AllergyReader {

    private static final String[] defaultAllergies = {
        "Oxybenzone • Benzophone-3 • 2-hydroxy-4-methoxy-benzophenone • 2-benzoyl-5-methoxyphenol • Eusolex 4360 • Escalol 567 • Cyasorb UV9",
        "BHT • Butylated hydroxytoluene • Butyl hydroxytoluene • 2,6-ditert-butyl-4-cresol • dibutyl paracresol • 6-ditert-butyl-4-cresol",
        "Lidocaine • 2-(Diethylamino)-N-(2,6-dimethylpheny)acetamide • 2-Diethylamino-2’,6’-acetoxylidide • w-Diethylamino-2’,6’-dimethylacetanilide • Anestacon • Cuivasal • Duncaine • EMLA(R) • Gravocain • Isicaine • Lignocaine • Lidothesin • Leostesin • Rucaina • Sylestesin • Xylocitin • Xylocaine • Xylotox • Xylestesin",
        "Methylisothiazolinone • Methylchloroisothiazolinone • 5-chloro-2-methyl-4-isothiazolin-3-one • 2-methyl-4-isothiazolin-3-one • Kathon CG • Euxyl K100 • Groton K",
        "Shellac • Candy glaze • Confectioner’s glaze • Lac • Lac resin • Lacca • Gommelaque • Schellack • Shellac, purified • Shellac glaze",
        "Sorbitan oleate • Sorbitan monooleate • Alkamulus SMO • Arlacel 80 • Armotan MO • Atmer 05 • Crill 4 • Dehymulus SMO • Disponil 100 • Emasol • Emsorb 2500 • Glycomul O • HSDB 5822 • Ionet S-80 • Kemmat S 80 • Kosteran O 1 • Lonzest SMO • Mono 9 octadecenoate • Monodehydrosorbitol monooleate • Montn 80, Montane 80 VGA • Newcol 80 • Nikkol SO 10, 15 • Nissan Nonion OP 80R • Oleate de sorbitan • Radiasurf 7155 • Rheodol AO, SP • Rikemal O 250 • Sorbester P 17 • Sorbitan • Sorbitan oleate • Span 80",
        "Thimerosal • Benzoic acid • Elcide • Ethylmercurithiosalicylic acid sodium salt • Mercurothiolate • Merfamin • Merseptyl • Merthiolate • Mertorgan • Merzonin • Merzonin sodium • Nosemack • SET • Sodium ethylmercuric thiosalicylate • Thiomersalate",
        "Tween 80 • Polysorbate 80 • Polyoxyethylenesorbitanmonooleate • Armotan pmo 20 • Campmul poe o • Drewmulse poesmo • Emsorb 6900 • Glycosperse 0 20 • Glycosperse 0 20 veg • Glycosperse 0 20x • Liposorb 0 20 • Olothorb • POE (5), (20) sorbitan monooleate • Polyoxyethylene oxide sorbitan monooleate • Polysorbate 80 b.p.c. • Polysorbate 80 • Polyoxyethylene (5) sorbitan monooleate • Protasorb o 20 • Sorbitan mono oleate polyoxyethylene • Sorlate • Sorethytan (20) mono oleate • Sorbitan, (x) Sorbitan • Sorbitan, monooleate polyoxyethylene • Sorbitan, mono 9 octadecanoate • Sorbimacrogol oleate 300"
    };

    private List<String> allergies;

    public AllergyReader(String filename) {
        try {
            BufferedReader reader = new BufferedReader(new FileReader(filename));
            allergies = reader.lines().collect(Collectors.toList());
        } catch (IOException e) {
            allergies = Arrays.asList(defaultAllergies);
        }
    }

    public Stream<String> readAllAllergies() {
        return allergies.stream();
    }
}
