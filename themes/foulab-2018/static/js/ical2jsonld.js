async function ical2jsonld() {
  let script = document.createElement('script');
  script.src = window.baseRoot + '/js/calendar/ical.min.js';
  document.head.appendChild(script);
  await new Promise((resolve, reject) => {
    script.addEventListener('load', resolve);
    script.addEventListener('error', reject);
  });

  const response = await fetch('../ical/foulab.ics');
  const text = await response.text();

  var jcalData = ICAL.parse(text);
  var vcalendar = new ICAL.Component(jcalData);
  for (const vevent of vcalendar.getAllSubcomponents('vevent')) {
    let object = {
      '@context': 'https://schema.org',
      '@type': 'Event',
    };
    object['name'] = vevent.getFirstPropertyValue('summary');
    function isoFromIcal(v) {
      let iso = v.toString();
      // TODO: time zone. Doesn't work with old ical, does work with v2.0.1.
      /*
      if (!v.isDate) {
        iso += 'Z' + Math.floor(v.utcOffset() / 3600).toString() +
          ':' + Math.floor((v.utcOffset() % 3600) / 60).toString().padStart(2, '0');
      }
      */
      return iso;
    }
    object['startDate'] = isoFromIcal(vevent.getFirstPropertyValue('dtstart'));
    object['endDate'] = isoFromIcal(vevent.getFirstPropertyValue('dtend'));
    object['location'] = {
      "@type": "Place",
      "name": "Foulab",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "999 du Collège",
        "addressLocality": "Montreal",
        "postalCode": "H4C 2S2",
        "addressRegion": "QC",
        "addressCountry": "CA"
      },
    };
    object['image'] = 'https://foulab.org/img/logo.png';
    object['description'] = vevent.getFirstPropertyValue('description'),
      object['offers'] = {
        '@type': 'Offer',
        'price': 0,
      };

    let script = document.createElement('script');
    script.setAttribute('type', 'application/ld+json');
    script.innerText = JSON.stringify(object);
    document.body.appendChild(script);

    const icaldebug = (new URLSearchParams(location.search)).get('icaldebug') != null;
    if (icaldebug) {
      let pre = document.createElement('pre');
      pre.innerText = JSON.stringify(object, null, 2);
      document.body.appendChild(pre);
    }
  }
}
