import java.util.Arrays;
import java.util.Optional;

public class AllergyChecker {

    private AllergyReader reader;

    public AllergyChecker(AllergyReader reader) {
        this.reader = reader;
    }

    public Optional<String> getAllergyIfFound(final String ingredient) {
        return reader.readAllAllergies()
                .map(s -> Arrays.asList(s.toUpperCase().split(" • ")))
                .filter(list -> list.contains(ingredient.toUpperCase()))
                .map(list -> String.join(" • ", list))
                .findFirst();
    }
}
