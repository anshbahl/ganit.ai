let form = document.querySelector('form');
let promptInput = document.querySelector('input[name="prompt"]');
let output = document.querySelector('.output');

form.onsubmit = async (ev) => {
  ev.preventDefault();
  output.textContent = 'Generating...';

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gemini-1.5-flash',
        contents: [
          {
            type: 'text',
            text: promptInput.value
          }
        ]
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';
    const md = new markdownit();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.startsWith('data:'));
      for (let line of lines) {
        const json = JSON.parse(line.replace('data:', '').trim());
        fullText += json.text;
        output.innerHTML = md.render(fullText);
      }
    }

  } catch (e) {
    output.innerHTML += '<hr>Error: ' + e;
  }
};
