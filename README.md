# Opravidlo Annotations

A tool for generating and annotating Czech language examples for training a grammar checker Opravidlo 2.0.

## Project Overview

Opravidlo Annotations is designed to help create annotated examples of Czech language phenomena by:

1. Fetching concordances (text examples) from corpus query systems (Kontext and Sketch Engine)
2. Processing these examples to extract relevant sentences
3. Annotating the sentences to highlight specific language phenomena
4. Saving the annotated examples in text and Word formats with accompanying logs of queries

## Code Structure

The project is organized into several modules:

### Core Modules
- `main.py`: The entry point for the application, containing configuration for queries
- `core/generate_concordances.py`: Handles fetching concordances from corpus query systems
- `core/concordance2annotation.py`: Processes concordances and adds annotations

### API Modules
- `api/kontext.py`: Interface for the Kontext corpus query system
- `api/sketch_engine.py`: Interface for the Sketch Engine corpus query system

### Utility Modules
- `utils/utils.py`: General utility functions for file handling and text processing
- `utils/query_logs.py`: Functions for logging queries and generating documentation

### Configuration
- `settings.py`: Contains configuration settings, including API tokens and file paths

## How to Use

### Prerequisites
1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables for API access:
   - Create a `.env` file in the project root
   - Add your API tokens:
     ```
     KONTEXT_TOKEN=your_kontext_token
     SKETCH_ENGINE_TOKEN=your_sketch_engine_token
     SKETCH_ENGINE_USERNAME=your_sketch_engine_username
     ```

### Basic Usage

1. Configure your query in `main.py`:
   ```python
   # Set corpus manager and corpus name
   corpus_manager = "kontext"  # Options: "kontext", "sketch", "combo"
   corpus_name = "syn2020"     # Corpus name depends on the manager
   
   # Define target word and its variants
   target = "jejích"
   variants = ["jejich"]
   is_target_valid = False  # Is the target orthographically correct?
   
   # Define the corpus query
   query = '[lemma="jejích" & tag=".*"]'
   
   # Set number of concordances to fetch
   number_of_concordances_to_fetch = 80
   number_of_concordances_to_log = 10
   
   # Set output filename
   filename = "jejích_jejich"
   ```

2. Run the script:
   ```
   python -m opravidlo_annotations.main
   ```

3. The script will:
   - Fetch concordances from the specified corpus
   - Process and annotate the concordances
   - Save the results to text and Word files
   - Generate documentation of queries in JSON and text formats

### Output Format

The annotated sentences will be in the format:
```
Beginning of the sentence [*error|correct|corpus*] rest of the sentence.
```

For example:
```
Stál před [*jejích|jejich|corpus*] chalupou.
```

### Additional features

- Use the `combo` corpus manager to fetch examples from multiple corpora
- Customize annotation format by modifying the `add_annotation_to_sentence` function
- Create custom target variant constructors for complex language phenomena

## Example Workflow

1. Set up a query for a specific language phenomenon
2. Run the script to generate annotated examples
3. Review the examples in the generated text or Word files
4. Use the check function to verify the distribution of variants
5. Use the generated examples as training data for Opravidlo 2.0