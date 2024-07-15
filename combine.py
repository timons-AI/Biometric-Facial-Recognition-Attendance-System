import os

def combine_text_files(input_folder, output_file):
    """
    Combine all text files in the input folder into a single output file
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(input_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(input_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(f"\n\n--- Content from {filename} ---\n\n")
                    outfile.write(infile.read())
                print(f"Added content from {filename}")

# Specify the input folder and output file
input_folder = "scraped_content"
output_file = "combined_content.txt"

# Run the function
combine_text_files(input_folder, output_file)
print(f"All text files have been combined into {output_file}")