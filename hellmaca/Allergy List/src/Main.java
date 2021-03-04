import java.io.FileNotFoundException;
import java.util.List;
import java.util.Optional;
import java.util.Scanner;

public class Main {

    private static final String ALLERGIES_FILE = "allergies.txt";
    private static final String DEFAULT_INGREDIENT_FILE = "ingredients.txt";

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        String choice;
        do {
            System.out.println("Choose option between (F)ile and (C)onsole:");
            choice = in.nextLine().trim();
        } while (!choice.matches("(?i:f(ile)?)") && !choice.matches("(?i:c(onsole)?)"));


        boolean dangerous = false;
        AllergyReader allergyReader = new AllergyReader(ALLERGIES_FILE);
        AllergyChecker allergyChecker = new AllergyChecker(allergyReader);

        if (choice.matches("(?i:f(ile)?)")) {
            System.out.println("Ingredient file name:");
            String filename = in.nextLine().trim();

            List<String> ingredientsList = null;
            try {
                ingredientsList = new IngredientsReader(filename).ingredientsList();
            } catch (FileNotFoundException e){
                System.err.println("Ingredient file does not exist, using default file");
                try {
                    ingredientsList = new IngredientsReader(DEFAULT_INGREDIENT_FILE).ingredientsList();
                } catch (FileNotFoundException e1) {
                    System.err.println("Default file not found, exiting");
                    System.exit(1);
                }
            }

            for (String ingredient : ingredientsList) {
                dangerous |= checkIngredient(allergyChecker, ingredient);
            }
        } else {
            while (true) {
                System.out.println("Ingredient to check (exit to quit):");
                String ingredient = in.nextLine().trim();

                if (ingredient.equalsIgnoreCase("exit")) {
                    break;
                }

                dangerous |= checkIngredient(allergyChecker, ingredient);
            }
        }

        if (dangerous) {
            System.out.println("This is not a safe food to ingest.");
        } else {
            System.out.println("This is a safe food to ingest.");
        }
    }

    private static boolean checkIngredient(AllergyChecker allergyChecker, String ingredient) {
        Optional<String> allergen = allergyChecker.getAllergyIfFound(ingredient);
        if (allergen.isPresent()) {
            System.out.println("Found " + allergen.get() + " in ingredient list.");
            return true;
        } else {
            return false;
        }
    }
}
