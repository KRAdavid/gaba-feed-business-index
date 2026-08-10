(() => {
  'use strict';

  const productCopy = {
    crude: {
      intro: 'GABA 20% 기준으로 사료회사와 농장의 축종별 배합 설계를 검토하는 원료형 솔루션입니다.',
      stats: [['GABA 기준', '20%'], ['가격 상태', '견적 확인'], ['배합 기준', '활성 GABA 기준']],
      note: '가바크루드는 자체 배합이나 축종별 프리믹스 개발을 검토하는 사료회사에 적합합니다. 최종 가격과 공급조건은 개별 견적으로 확인합니다.'
    },
    caremix: {
      intro: '가바크루드와 미네랄 매트릭스를 조합해 사료회사의 브랜드 제품으로 검토하는 OEM·ODM형 배합사료 솔루션입니다.',
      note: '가바케어믹스는 자체 연구개발 부담을 줄이고 기능성 브랜드 사료를 검토하려는 사료회사에 적합합니다.'
    }
  };

  function applyProductCopy() {
    const active = document.querySelector('[data-product].active');
    const key = active?.dataset.product || 'crude';
    const copy = productCopy[key];
    if (!copy) return;
    const intro = document.getElementById('productIntro');
    const note = document.getElementById('productNote');
    if (intro) intro.textContent = copy.intro;
    if (note) note.textContent = copy.note;
    if (copy.stats) {
      const stats = document.getElementById('productStats');
      if (stats) stats.innerHTML = copy.stats.map(([label, value]) => `<div><small>${label}</small><strong>${value}</strong></div>`).join('');
    }
  }

  window.addEventListener('load', () => {
    applyProductCopy();
    document.querySelectorAll('[data-product]').forEach((button) => button.addEventListener('click', () => setTimeout(applyProductCopy, 0)));
  });
})();
