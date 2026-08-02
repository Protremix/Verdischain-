import { createClientFromRequest } from 'npm:@base44/sdk@0.8.31';

Deno.serve(async (req) => {
  try {
    const base44 = createClientFromRequest(req);
    
    const resp = await fetch('https://verdischain.com/api/monitor/status');
    
    if (!resp.ok) {
      return new Response(JSON.stringify({
        healthy: false,
        status: 'unreachable',
        severity: 'CRITICAL',
        message: 'Blockchain API returned ' + resp.status
      }), { headers: { 'Content-Type': 'application/json' } });
    }
    
    const data = await resp.json();
    const isHealthy = data.status === 'healthy' && data.chainValid === true;
    
    return new Response(JSON.stringify({
      healthy: isHealthy,
      status: data.status || 'unknown',
      blockHeight: data.blockHeight || 0,
      chainValid: data.chainValid || false,
      blockStalenessMs: data.blockStalenessMs || 999999,
      mempoolSize: data.mempoolSize || 0,
      validatorCount: data.validatorCount || 0,
      uptime: data.uptime || 0,
      recentAlerts: data.recentAlerts || [],
      severity: isHealthy ? 'OK' : 'WARNING',
      message: isHealthy ? 'Blockchain is healthy' : 'Blockchain issue detected: status=' + (data.status || 'unknown') + ', chainValid=' + (data.chainValid || false)
    }), { headers: { 'Content-Type': 'application/json' } });
  } catch (e) {
    return new Response(JSON.stringify({
      healthy: false,
      status: 'error',
      severity: 'CRITICAL',
      message: e.message || 'Unknown error'
    }), { headers: { 'Content-Type': 'application/json' } });
  }
});
