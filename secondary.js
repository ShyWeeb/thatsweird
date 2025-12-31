document.addEventListener('DOMContentLoaded', function() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');

    question.addEventListener('click', function() {
      // Toggle active class
      item.classList.toggle('active');

      // Toggle ARIA attributes
      this.setAttribute('aria-expanded', item.classList.contains('active'));
      answer.style.display = item.classList.contains('active') ? 'block' : 'none';
    });
  });
});
