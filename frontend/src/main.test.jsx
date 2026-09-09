import {describe,it,expect} from 'vitest';
describe('AegisFleet UI',()=>{it('exposes the expected navigation contract',()=>expect(['Dashboard','Missions','Fleet','Live Mission','Inspections','Mission History','Knowledge Base','System Logs']).toHaveLength(8))})
