import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.List;
import java.util.stream.Collectors;

public class IngredientsReader {

    private BufferedReader reader;

    public IngredientsReader(String filename) throws FileNotFoundException {
        reader = new BufferedReader(new FileReader(filename));
    }

    public List<String> ingredientsList() {
        return reader.lines().collect(Collectors.toList());
    }
}
