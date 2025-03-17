from dataclasses import dataclass
import os
from curl_cffi import requests
from typing import List, Tuple
import concurrent.futures
import shutil
import img2pdf
import typer
from rich.console import Console
from tqdm import tqdm

app = typer.Typer(help="MangaDex Downloader - Download manga chapters from MangaDex")
console = Console()


@dataclass
class MangaDex:
    manga_url: str
    language: str = "pt-br"
    output_dir: str = "output"
    temp_dir: str = "temp"
    max_retries: int = 3

    def __get_feed_size(self):
        manga_id = self.manga_url.split("/")[-2]

        headers = {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "dnt": "1",
            "origin": "https://mangadex.org",
            "priority": "u=1, i",
            "referer": "https://mangadex.org/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        }

        response = requests.get(
            f"https://api.mangadex.org/manga/{manga_id}/feed?limit=1&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic",
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception("Incapaz de obter total de capitulos.")

        data = response.json()

        # Check if we have data and at least one chapter
        if "data" not in data or not data["data"]:
            return 0

        first_chapter = data["data"][0]
        if (
            "attributes" not in first_chapter
            or "chapter" not in first_chapter["attributes"]
        ):
            return 0

        # Get the chapter number and convert to integer
        try:
            chapter_number = int(float(first_chapter["attributes"]["chapter"]))
            self.feed_size = chapter_number * 4
            print(f"Total chapters found: {chapter_number}")
        except (ValueError, TypeError):
            print("Failed to parse chapter number")
            return 0

    def get_chapters(self):
        manga_id = self.manga_url.split("/")[-2]

        self.__get_feed_size()

        headers = {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "dnt": "1",
            "origin": "https://mangadex.org",
            "priority": "u=1, i",
            "referer": "https://mangadex.org/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

        response = requests.get(
            f"https://api.mangadex.org/manga/{manga_id}/feed?limit={self.feed_size}&includes[]=scanlation_group&includes[]=user&order[volume]=desc&order[chapter]=desc&offset=0&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic",
            headers=headers,
        )
        
        if response.status_code != 200:
            raise Exception("MangaDex fora do ar ou em manutenção.")

        chapters = response.json()
        
        # Extract chapter IDs that match the specified language
        self.chapters = {}
        if "data" in chapters:
            for chapter in chapters["data"]:
                if (
                    chapter["attributes"]["translatedLanguage"].lower()
                    == self.language.lower()
                ):
                    self.chapters[f"Capítulo {chapter['attributes']['chapter']}"] = (
                        chapter["id"]
                    )
        else:
            print("No chapters data found in the response")
    
    def download_chapter(self, chapter_id: str, chapter_name: str = None):
        chapter_pages, chapter_hash = self.get_chapter_pages(chapter_id)
        headers = {
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Referer": "https://mangadex.org/",
            "Referrer-Policy": "strict-origin",
        # You might want to keep these from your existing headers for consistency
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "accept": "*/*",
        }

        # Add chapter name to the progress bar description
        desc = (
            f"Downloading {chapter_name}"
            if chapter_name
            else f"Downloading chapter {chapter_id}"
        )
        for page in tqdm(chapter_pages, desc=desc):
            page_url = (
                f"https://cmdxd98sb0x3yprd.mangadex.network/data/{chapter_hash}/{page}"
            )
            response = requests.get(
                page_url,
                headers=headers,
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {response.status_code}")
            
            if not os.path.exists(f"{self.temp_dir}/{chapter_name.replace(' ', '')}"):
                os.makedirs(f"{self.temp_dir}/{chapter_name.replace(' ', '')}")

            # Extract only numbers from chapter_name

            with open(
                f"{self.temp_dir}/{chapter_name.replace(' ', '')}/{page.split('-')[0]}.jpg",
                "wb",
            ) as f:
                f.write(response.content)

        return chapter_id

    def get_chapter_pages(self, chapter_id: str) -> Tuple[List[str], str]:
        headers = {
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "dnt": "1",
            "origin": "https://mangadex.org",
            "priority": "u=1, i",
            "referer": "https://mangadex.org/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }
        
        params = {
            "forcePort443": "false",
        }

        response = requests.get(
            f"https://api.mangadex.org/at-home/server/{chapter_id}",
            params=params,
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(
                "Erro ao obter capitulo. Status da requisição: "
                + str(response.status_code)
            )
    
        return response.json()["chapter"]["data"], response.json()["chapter"]["hash"]
    
    def download_manga(self, retry_count=0, chapters_to_retry=None):
        # If this is a retry, use the chapters passed in
        if chapters_to_retry:
            self.chapters = chapters_to_retry
        # Otherwise, get all chapters for the first time
        elif not hasattr(self, "chapters") or not self.chapters:
            self.get_chapters()

        if not self.chapters:
            print("No chapters found for the specified language.")
            return

        # Create output directories if they don't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        total_chapters = len(self.chapters)

        # Show appropriate message based on whether this is an initial run or retry
        if retry_count == 0:
            print(f"Found {total_chapters} chapters to download")
        else:
            print(
                f"Retry attempt {retry_count}/{self.max_retries}: Retrying {total_chapters} chapters"
            )

        # Track failed chapters
        failed_chapters_dict = {}

        # Use ThreadPoolExecutor to download chapters in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Create a dictionary mapping futures to chapter names for better progress reporting
            future_to_chapter = {
                executor.submit(self.download_chapter, chapter_id, chapter_name): (
                    chapter_name,
                    chapter_id,
                )
                for chapter_name, chapter_id in self.chapters.items()
            }

            # Progress bar label based on retry status
            progress_desc = (
                f"Retry attempt {retry_count}"
                if retry_count > 0
                else "Downloading chapters"
            )

            # Process completed downloads as they finish with a progress bar
            with tqdm(
                total=total_chapters, desc=progress_desc, unit="chapter"
            ) as progress_bar:
                for future in concurrent.futures.as_completed(future_to_chapter):
                    chapter_name, chapter_id = future_to_chapter[future]
                    try:
                        chapter_id = (
                            future.result()
                        )  # This will raise any exceptions that occurred

                        # Get temp directory where images were saved
                        temp_chapter_dir = (
                            f"{self.temp_dir}/{chapter_name.replace(' ', '')}"
                        )

                        if os.path.exists(temp_chapter_dir):
                            # Convert chapter to PDF before moving
                            self.convert_chapter_to_pdf(temp_chapter_dir, chapter_name)

                            # No longer copying image files to output directory
                            # Just delete the temp directory with all images
                            shutil.rmtree(temp_chapter_dir)

                        progress_bar.update(1)
                        progress_bar.set_postfix_str(f"Last: {chapter_name}")
                    except Exception as e:
                        # Store failed chapter in dictionary to retry
                        failed_chapters_dict[chapter_name] = chapter_id
                        progress_bar.update(1)
                        progress_bar.set_postfix_str(f"Failed: {chapter_name}")
                        print(f"\n❌ Failed to download {chapter_name}: {str(e)}")

        # Print summary information about this download attempt
        successful_chapters = total_chapters - len(failed_chapters_dict)
        if retry_count == 0:
            print(
                f"\nDownload attempt complete: {successful_chapters}/{total_chapters} chapters downloaded successfully."
            )
        else:
            print(
                f"\nRetry attempt {retry_count} complete: {successful_chapters}/{total_chapters} chapters recovered."
            )

        # If we have failed chapters and haven't exceeded max retries, retry them
        if failed_chapters_dict and retry_count < self.max_retries:
            print(f"\nRetrying {len(failed_chapters_dict)} failed chapters...")
            self.download_manga(retry_count + 1, failed_chapters_dict)
        # Otherwise print the final status
        elif failed_chapters_dict:
            print(
                f"\n{len(failed_chapters_dict)} chapters still failed after {self.max_retries} retry attempts:"
            )
            for chapter_name, chapter_id in failed_chapters_dict.items():
                print(f"❌ {chapter_name}")
        else:
            print("\nAll chapters downloaded successfully!")

    def convert_chapter_to_pdf(self, image_dir, chapter_name):
        """Convert a directory of images to a single PDF file"""

        # Get all jpg files
        image_files = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]

        # Sort the files using natural sort (handles alphanumeric properly)
        def natural_sort_key(s):
            import re

            def atoi(text):
                return int(text) if text.isdigit() else text

            return [atoi(c) for c in re.split(r"(\d+)", s)]

        image_files.sort(key=natural_sort_key)

        # Full paths to images
        image_paths = [os.path.join(image_dir, img) for img in image_files]

        if not image_paths:
            print(f"No images found in {image_dir}")
            return

        # Create PDF filename
        pdf_filename = f"{chapter_name}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        try:
            # Convert images to PDF
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(img2pdf.convert(image_paths))
            print(f"Created PDF: {pdf_filename}")
        except Exception as e:
            print(f"Error creating PDF for {chapter_name}: {str(e)}")


@app.command()
def mangadex_dl(
    url: str = typer.Argument(..., help="The MangaDex URL of the manga to download"),
    language: str = typer.Option(
        "pt-br", help="Language code for the manga chapters (e.g., pt-br, en)"
    ),
    output_dir: str = typer.Option(
        "output", help="Directory to save the downloaded manga"
    ),
    max_retries: int = typer.Option(
        3, help="Maximum number of retry attempts for failed downloads"
    ),
):
    """
    Download manga chapters from MangaDex.
    """
    try:
        manga = MangaDex(
            manga_url=url,
            language=language,
            output_dir=output_dir,
            max_retries=max_retries,
        )
        
        # Create a progress bar for the overall download
        with tqdm(total=1, desc="Downloading manga", unit="manga") as pbar:
            manga.download_manga()
            pbar.update(1)
            
        console.print("[green]✓[/green] Download completed successfully!")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def version():
    """
    Show the version of the application.
    """
    console.print("MangaDex Downloader v0.1.0")

        
if __name__ == "__main__":
    app()
    