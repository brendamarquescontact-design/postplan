// Melhorias progressivas: o site funciona sem JavaScript.
(function () {
  // Confirmação antes de ações destrutivas (IHC: prevenir erros / ações reversíveis)
  document.querySelectorAll("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      if (!window.confirm(form.dataset.confirmar)) ev.preventDefault();
    });
  });

  // Filtros aplicam ao escolher uma opção
  document.querySelectorAll("select[data-auto-submit]").forEach(function (sel) {
    sel.addEventListener("change", function () { sel.form.submit(); });
  });

  // Contador de caracteres do roteiro
  document.querySelectorAll("textarea[data-contador]").forEach(function (ta) {
    var alvo = document.getElementById(ta.dataset.contador);
    function atualizar() { if (alvo) alvo.textContent = ta.value.length; }
    ta.addEventListener("input", atualizar);
    atualizar();
  });
})();
