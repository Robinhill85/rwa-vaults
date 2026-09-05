const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('ledger/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1].replace(/loadData\(\);\s*$/,'');
const context=vm.createContext({document:{getElementById:()=>({addEventListener(){}}),addEventListener(){}},Date,console});
vm.runInContext(script,context);
const run=code=>vm.runInContext(code,context);
test('zero TVL is preserved and never replaced with a research estimate',()=>{
 assert.equal(run('tvlOf({live:{tvl_usd:0},tvl_usd_approx:999}).n'),0);
 assert.equal(run('fmtUsd(0.004)'),'<$0.01');
 assert.equal(run('fmtUsd(null)'),'Unavailable');
});
test('live, approx, snapshot and unavailable classify independently',()=>{
 assert.equal(run('statusOf(0,new Date().toISOString())'),'live');
 assert.equal(run('statusOf(2,"2020-01-01")'),'snapshot');
 assert.equal(run('statusOf(2,null)'),'snapshot');
 assert.equal(run('statusOf(2,"2020-01-01","approx")'),'approx');
 assert.equal(run('statusOf(null,new Date().toISOString())'),'unavailable');
});
test('legacy CMC zeros stay unknown; v2 preserves confirmed zero',()=>{
 assert.equal(run('legacyCmc(0,{})'),null);
 assert.equal(run('legacyCmc(0,{schema_version:2})'),0);
 assert.equal(run('percent(-1.23)'),'−1.23%');
 assert.equal(run('percent(1.23)'),'+1.23%');
});
test('eligibility combines region, budget and KYC and excludes unknown minimums',()=>{
 context.fixture=[
  {id:'retail',access:{regions:{us:true},min_usd:100},terms:{kyc:'kyc_retail'}},
  {id:'wallet',access:{regions:{us:true},min_usd:100},terms:{kyc:'none'}},
  {id:'large',access:{regions:{us:true},min_usd:50000},terms:{kyc:'none'}},
  {id:'eu',access:{regions:{us:false},min_usd:100},terms:{kyc:'none'}},
 ];
 assert.equal(run('state.region="us";fixture.filter(eligible).length'),3);
 assert.equal(run('state.ticket=10000;fixture.filter(eligible).length'),2);
 assert.equal(run('state.kyc="none";fixture.filter(eligible).length'),1);
 assert.equal(run('eligible({id:"test",access:{regions:{us:true}},terms:{kyc:"none"}})'),false);
});
