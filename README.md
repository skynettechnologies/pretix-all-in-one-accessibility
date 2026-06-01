# **All in One Accessibility® - Pretix Accessibility Plugin**

## **Free WCAG, ADA, EAA accessibility plugin for Pretix websites!**

This [Free Pretix accessibility plugin](https://www.skynettechnologies.com/pretix-accessibility-widget) - adds an accessible experience for users with visual, auditory, motor, or cognitive disabilities. It supports assistive technologies, offers customizable updates, and enhances overall usability according to WCAG 2.1, 2.2, ADA, EAA, Section 508, France RGAA, California Unruh, European EAA EN 301 549, UK Equality Act, Spain UNE 139803:2012, Australian DDA, Israeli Standard 5568, Ontario AODA, Canada ACA, German BITV, Brazilian Inclusion Law (LBI 13.146/2015), JIS X 8341 (Japan), Italian Stanca Act, Indian RPwD Act, Switzerland DDA and other [accessibility standards](https://www.skynettechnologies.com/accessibility-standards).

This [free accessibility widget](https://www.skynettechnologies.com/free-website-accessibility-widget) quickly add essential accessibility features through a lightweight, easy to install solution that supports inclusive browsing and compliance efforts.

**Core Features - What you get with free accessibility Pretix widget?**

- Auto-detect language
- Supports 190+ multi-languages.
- Skip to Navigation / Content / Footer
- Content Adjustment Options
- Visual & Color Adjustments
- Dynamic free Pretix accessibility module customization including colors, size, icon, and position
- Reading mask
- Accessibility statement

Explore the [free accessibility widget features guide](https://www.skynettechnologies.com/sites/default/files/Free-Accessibility-Widget-Features-Guide.pdf).

**This free accessibility Pretix plugin is a great fit for:**

- Businesses, developers, agencies, content teams, ecommerce brands, educational institutions, and public-facing organizations using Pretix who want to improve WCAG accessibility, usability, and user experience quickly without complex development.

**Why select free Pretix WCAG accessibility module - All in One Accessibility?**

- Supports alignment with global accessibility standards
- Improves usability for users with visual, cognitive, and motor impairments.
- Integrates smoothly with most Pretix themes.
- Supports 190 plus multi languages and multisite for global accessibility reach.
- Available at no cost for core accessibility features.

### **SECURITY & PRIVACY NOTES**

- This Free Accessibility Pretix module follows several data and application security practices, including ISO 9001:2015 & ISO 27001:2013, GDPR, CCPA, COPPA, HIPAA, and SOC 2 Type II.
- Skynet Technologies USA LLC is an organizational member of IAAP and of W3C.
- No personal data is intentionally stored by the module itself. Site owners are responsible for reviewing their own compliance requirements.

### **LIMITATIONS**

- Some advanced features require a commercial subscription.

For more details, visit [**Pretix accessibility plugin**](https://www.skynettechnologies.com/all-in-one-accessibility)**.**

## **FAQS**

**Is this AI accessibility extension compatible with Pretix multisite?**

Yes.

**Does this free Pretix accessibility plugin support multilingual Pretix sites?**

Yes. It supports 190+ languages.

**Which Pretix themes are supported by WCAG accessibility Pretix plugin?**

Major Pretix themes are supported by All in One Accessibility®.

**How can I upgrade from free to Paid Pretix accessibility widget for upgrading accessibility features?**

Upgrade to Paid subscription with **70 plus advanced features** and take website's accessibility to the next level. Checkout the steps for upgrading [free to paid Pretix accessibility widget](https://www.skynettechnologies.com/blog/upgrade-from-all-in-one-accessibility-free-widget-to-premium-version)**.**

**What additional features are available in the paid version of Pretix WCAG ADA EAA plugin?**

The paid version of Pretix accessibility widget includes following features like screen reader, voice navigation, talk & type, virtual keyboard, accessibility profiles tailored for different users with disabilities group, Libras (Brazilian sign language), dictionary search, multi-language support (190+ languages), and many more. Pricing starts from \$25 / month. Explore more information about [accessibility widget](https://www.skynettechnologies.com/all-in-one-accessibility) and buy now.

### **Supported Languages (190+ Languages)**

English (USA), English (UK), English (Australian), English (Canadian), English (South Africa), Español, Español (Mexicano), Deutsch, عربى, Português, Português (Brazil), 日本語, Français, Italiano, Polski, Pусский, 中文, 中文 (Traditional), עִברִית, Magyar, Slovenčina, Suomenkieli, Türkçe, Ελληνικά, Latinus, Български, Català, Čeština, Dansk, Nederlands, हिंदी, Bahasa Indonesia, 한국인, Lietuvių, Bahasa Melayu, Norsk, Română, Slovenščina, Svenska, แบบไทย, Українська, Việt Nam, বাঙালি, සිංහල, አማርኛ, Hmoob, မြန်မာ, Eesti keel, latviešu, Cрпски, Hrvatski, ქართული, ʻŌlelo Hawaiʻi, Cymraeg, Cebuano, Samoa, Kreyòl ayisyen, Føroyskt, Crnogorski, Azerbaijani, Euskara, Tagalog, Galego, Norsk Bokmål, فارسی, ਪੰਜਾਬੀ, shqiptare, Hայերեն, অসমীয়া, Aymara, Bamanankan, беларускі, bosanski, Corsu, ދިވެހި, Esperanto, Eʋegbe, Frisian, guarani, ગુજરાતી, Hausa, íslenskur, Igbo, Gaeilge, basa jawa, ಕನ್ನಡ, қазақ, ខ្មែរ, Kinyarwanda, Kurdî, Кыргызча, ພາສາລາວ, Lingala, Luganda, lëtzebuergesch, македонски, Malagasy, മലയാളം, Malti, Maori, मराठी, Монгол, नेपाली, Sea, ଓଡିଆ, Afaan Oromoo, پښتو, Runasimi, संस्कृत, Gàidhlig na h-Alba, Sesotho, Shona, سنڌي, Soomaali, basa Sunda, kiswahili, тоҷикӣ, தமிழ், Татар, తెలుగు, ትግሪኛ, Tsonga, Türkmenler, Ride, اردو, ئۇيغۇر, o'zbek, isiXhosa, יידיש, Yoruba, Zulu, भोजपुरी, डोगरी, कोंकणी, Kurdî, Krio, मैथिली, Meiteilon, Mizo tawng, Sepedi, Ilocano, دری

### **Installation Steps**

## Install Plugin

### Step 1 — Install the plugin

**From PyPI:**

```cmd
pip install pretix_all_in_one_accessibility
```

### Step 2 — Add to INSTALLED_APPS

Add in Django `settings.py` file, add:

```python
INSTALLED_APPS += [
    'pretix_all_in_one_accessibility',
]
```

### Step 3 — Collect static files

```cmd
python -m pretix collectstatic --noinput
```

### Step 4 — Run Migrations

```cmd
python manage.py migrate 
```

### Step 4 — Restart pretix

```cmd
python manage.py runserver
```

### Step 5 — Enable the plugin in the Pretix admin panel

1. Go to **Admin → Organizers → (your organizer) → Settings → Plugins**
2. Find **All In One Accessibility** and enable it
3. Navigate to **Organizer Settings → All In One Accessibility → Settings** to configure the widget

**Visit the Pretix Accessibility Improvements Demo to see how does it perform with improved accessibility features:**

<https://youtu.be/X70XtvGyvSs?si=RQpGHZS83ocQYqHV>

### **CORS Policy Configuration**

To avoid CORS policy issues, ensure the following URLs are allowed in your website. These URLs should be added to your CORS configuration or trusted domains list.

| **Domain** | **Description** | **Usage** |
| --- | --- | --- |
| https://\*.skynettechnologies.com | Skynet Technologies (Global Domain) | API access and resources |
| https://\*.skynettechnologies.us | Skynet Technologies (US Domain) | API access and resources |
| https://\*.googleapis.com | Google APIs | Services like Fonts, Translation |
| https://\*.gstatic.com | Fonts APIs | Custom Fonts |
| <https://vlibras.gov.br> | VLibras - Brazilian Sign Language Service | Sign Language |

### **Instructions**

- Update your server's CORS configuration to include these URLs.
- Ensure wildcard subdomains (\*) are supported where necessary.
- Verify the application functionality by testing requests to these domains.
- If issues persist, consult the documentation for CORS configuration guidance.

### **Documentation**

- [**Pretix WCAG compliance accessibility - Features Guide**](https://www.skynettechnologies.com/sites/default/files/accessibility-widget-features-list.pdf)

**Submit a Support Request**
Please visit our [**support page**](https://www.skynettechnologies.com/report-accessibility-problem) and fill out the form. Our team will get back to you as soon as possible.

**Send Us an Email**
Alternatively, you can send an email to our support team: [**hello@skynettechnologies.com**](mailto:hello@skynettechnologies.com)

**Accessibility Paid Add-on Services**
**[Pretix manual accessibility audit](https://www.skynettechnologies.com/website-accessibility-audit)**

- Enhance inclusivity and user experience by evaluating Pretix website's accessibility by [web accessibility consultant](https://www.skynettechnologies.com/web-accessibility-consultant).
- WCAG 2.0 / WCAG 2.1 / WCAG 2.2 Level AA conformance testing
- Automated, semi-automated testing
- Manual testing
- Simple before-after UI/UX recommendations on how to fix the issues
- Comprehensive audit report

**[Pretix site manual accessibility remediation](https://www.skynettechnologies.com/full-website-accessibility-remediation)**

Enhance Pretix website accessibility and inclusivity with our manual accessibility remediation add-on. This service includes fixing accessibility issues and thorough remediation of website manually. Our experts ensure accessibility with WCAG standards, improve user experience for those with disabilities, and provide a detailed report on the improvements made.

[**PDF/Document Accessibility Remediation**](https://www.skynettechnologies.com/pdf-accessibility-remediation)

The PDF / Document Remediation provides a list of inaccessible PDFs and remediated PDFs from where you can request PDF remediation service.

**[VPAT Report/Accessibility Conformance Report (ACR)](https://www.skynettechnologies.com/vpat-accessibility-conformance-report)**

The Voluntary Product Accessibility Template (VPAT), also known as an ACR (Accessibility Conformance Report) starts with an audit and provides current details for an accessible website, application, or any other digital assets.

**Accessibility Pretix Widget Paid Add-ons**
[**White Label Accessibility**](https://www.skynettechnologies.com/all-in-one-accessibility/addons#accessibility-widget-add-ons)

Remove the Skynet Technologies logo as well as all of the footer links, popups, report a problem link and more for full white label control.

[**Instant live site translations**](https://www.skynettechnologies.com/all-in-one-accessibility/addons#accessibility-widget-add-ons) **for Pretix sites**

Translate Pretix site into over 190 languages instantly to enhance accessibility for non-native speakers, individuals with language acquisition difficulties, and those with learning disabilities.

[**Modify Accessibility Menu**](https://www.skynettechnologies.com/all-in-one-accessibility/addons#accessibility-widget-add-ons) **for Pretix websites**

Build and fine-tune widget with the Modify Menu option. Reorder, remove and restructure the widget buttons to fit users' specific accessibility needs.

**Pretix Accessibility Partnership Opportunities**
[**Pretix accessibility agencies partnership**](https://www.skynettechnologies.com/agency-partners)

Partner with us as an agency to provide comprehensive Pretix ADA, EAA, WCAG accessibility solutions to clients. Get access to exclusive resources, training, and support to implement and manage accessibility features effectively.

[**Pretix accessibility affiliate partnership**](https://www.skynettechnologies.com/affiliate-partner)

Sign up for our affiliate program and earn commissions by promoting accessibility plugin. Share our widget with your network and help businesses improve their website accessibility while generating revenue.

For more details, explore [**Pretix accessibility partnership opportunities**](https://www.skynettechnologies.com/partner-program)

## Screenshots

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-1-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-2-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-3-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-4-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-5-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-6-free.jpg?v=4)

![App Screenshot](https://www.skynettechnologies.com/sites/default/files/screenshot-7-free.jpg?v=4)

## Video

[![All in One Accessibility](https://img.youtube.com/vi/I-DjgZyleeI/0.jpg)](https://www.youtube.com/watch?v=I-DjgZyleeI)

**Credits**
This addon is developed and maintained by [website accessibility remediation company](https://www.skynettechnologies.com/) - Skynet Technologies USA LLC

### **Current Maintainers**

- [**Skynet Technologies USA LLC**](https://github.com/skynettechnologies)