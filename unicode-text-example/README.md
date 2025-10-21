# Use Reve to make movie posters

To get text character forms to work better for non-ASCII languages, this
example renders the letters using a unicode font to a reference bitmap, and
provides it as reference to the /v1/images/remix endpoint.

## Usage

```bash
# Make a budget at api.reve.com/console, and then an API key for that budget.
export REVE_API_KEY=papi....

python3 makeimage.py --prompt "A swarthy man embraces a semi-clad demure woman, with a mysterious gothic church in the background. Hand drawn airbrushed illustration, movie poster." --output "image.png"

python3 makeposter.py --title "Ask not for whom the bodice rippeth, because it rippeth for you." --image "image.png" --output "poster.png"
```

This approach has about a 70% success rate, so you may need to generate more
than one combined output before you get an acceptable result, especially for
longer titles and output fonts that are vastly different from the Noto Sans
font used for illustration.

If you need CJK or emoji support, you may need to adapt this code to import and
use the appropriate fonts for those use cases.

## Initially generated image

![A swarthy man embraces a semi-clad demure woman, with a mysterious gothic church in the background. Hand drawn airbrushed illustration.](image.png)

![Ask not for whom the bodice rippeth, because it rippeth for you.](poster.png)

## Licenses

This code is made available under the MIT open source license, which is hereby
incorporated by reference. The copyright holders is &copy; Reve AI 2025, All Rights Reserved.

This repository contains a copy of the Noto-Sans font, available from Google
Fonts under the Open Fonts License.

