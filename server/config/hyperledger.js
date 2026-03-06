/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ HYPERLEDGER CONFIGURATION - INVESTOR-GRADE MODULE                         ║
  ║ Private blockchain network | Fabric v2.5 | Production-ready              ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/hyperledger.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-02
 */

import { Wallets, Gateway } from 'fabric-network';
import * as FabricCAServices from 'fabric-ca-client';
import path from 'path';
import fs from 'fs';

// ============================================================================
// NETWORK CONFIGURATION
// ============================================================================

const NETWORK_CONFIG = {
  channelName: process.env.HYPERLEDGER_CHANNEL || 'wilsy-channel',
  chaincodeName: process.env.HYPERLEDGER_CHAINCODE || 'document-anchor',
  mspId: process.env.HYPERLEDGER_MSP_ID || 'Org1MSP',
  
  peers: [
    {
      name: 'peer0.org1.example.com',
      url: process.env.PEER0_URL || 'grpcs://localhost:7051',
      tlsCACerts: path.join(__dirname, '../certificates/hyperledger/peer0/ca.crt')
    },
    {
      name: 'peer1.org1.example.com',
      url: process.env.PEER1_URL || 'grpcs://localhost:8051',
      tlsCACerts: path.join(__dirname, '../certificates/hyperledger/peer1/ca.crt')
    }
  ],

  orderer: {
    name: 'orderer.example.com',
    url: process.env.ORDERER_URL || 'grpcs://localhost:7050',
    tlsCACerts: path.join(__dirname, '../certificates/hyperledger/orderer/ca.crt')
  },

  ca: {
    name: 'ca.org1.example.com',
    url: process.env.CA_URL || 'https://localhost:7054',
    tlsCACerts: path.join(__dirname, '../certificates/hyperledger/ca/ca.crt')
  },

  timeout: parseInt(process.env.HYPERLEDGER_TIMEOUT) || 300,
  connectionRetries: parseInt(process.env.HYPERLEDGER_RETRIES) || 3
};

// ============================================================================
// CONNECTION PROFILE
// ============================================================================

export const connectionProfile = {
  name: 'wilsy-hyperledger-network',
  version: '1.0.0',
  client: {
    organization: 'Org1',
    connection: {
      timeout: {
        peer: {
          endorser: NETWORK_CONFIG.timeout.toString(),
          eventHub: NETWORK_CONFIG.timeout.toString(),
          eventReg: NETWORK_CONFIG.timeout.toString()
        },
        orderer: NETWORK_CONFIG.timeout.toString()
      }
    }
  },
  channels: {
    [NETWORK_CONFIG.channelName]: {
      orderers: [NETWORK_CONFIG.orderer.name],
      peers: NETWORK_CONFIG.peers.reduce((acc, peer) => ({
        ...acc,
        [peer.name]: {
          endorsingPeer: true,
          chaincodeQuery: true,
          ledgerQuery: true,
          eventSource: true
        }
      }), {})
    }
  },
  organizations: {
    Org1: {
      mspid: NETWORK_CONFIG.mspId,
      peers: NETWORK_CONFIG.peers.map(p => p.name),
      certificateAuthorities: [NETWORK_CONFIG.ca.name]
    }
  },
  orderers: {
    [NETWORK_CONFIG.orderer.name]: {
      url: NETWORK_CONFIG.orderer.url,
      grpcOptions: {
        'ssl-target-name-override': NETWORK_CONFIG.orderer.name,
        'grpc.keepalive_time_ms': 120000,
        'grpc.default_authority': NETWORK_CONFIG.orderer.name
      },
      tlsCACerts: {
        path: NETWORK_CONFIG.orderer.tlsCACerts
      }
    }
  },
  peers: NETWORK_CONFIG.peers.reduce((acc, peer) => ({
    ...acc,
    [peer.name]: {
      url: peer.url,
      grpcOptions: {
        'ssl-target-name-override': peer.name,
        'grpc.keepalive_time_ms': 120000,
        'grpc.default_authority': peer.name
      },
      tlsCACerts: {
        path: peer.tlsCACerts
      }
    }
  }), {}),
  certificateAuthorities: {
    [NETWORK_CONFIG.ca.name]: {
      url: NETWORK_CONFIG.ca.url,
      caName: NETWORK_CONFIG.ca.name,
      tlsCACerts: {
        path: NETWORK_CONFIG.ca.tlsCACerts
      },
      httpOptions: {
        verify: false
      }
    }
  }
};

// ============================================================================
// WALLET MANAGEMENT
// ============================================================================

export const getWallet = async () => {
  const walletPath = path.join(__dirname, '../certificates/hyperledger/wallet');
  return await Wallets.newFileSystemWallet(walletPath);
};

export const getGateway = async (identityName = 'admin') => {
  const wallet = await getWallet();
  const gateway = new Gateway();

  await gateway.connect(connectionProfile, {
    wallet,
    identity: identityName,
    discovery: { enabled: true, asLocalhost: true }
  });

  return gateway;
};

export const getContract = async (identityName = 'admin') => {
  const gateway = await getGateway(identityName);
  const network = await gateway.getNetwork(NETWORK_CONFIG.channelName);
  const contract = network.getContract(NETWORK_CONFIG.chaincodeName);
  return { contract, gateway };
};

export const getCA = async () => {
  const caInfo = connectionProfile.certificateAuthorities[NETWORK_CONFIG.ca.name];
  return new FabricCAServices(caInfo.url, { 
    trustedRoots: caInfo.tlsCACerts.path,
    verify: false 
  }, caInfo.caName);
};

export const enrollAdmin = async () => {
  try {
    const ca = await getCA();
    const wallet = await getWallet();

    const adminIdentity = await wallet.get('admin');
    if (adminIdentity) {
      console.log('✅ Admin identity already exists');
      return adminIdentity;
    }

    const enrollment = await ca.enroll({ 
      enrollmentID: 'admin', 
      enrollmentSecret: 'adminpw' 
    });

    const identity = {
      credentials: {
        certificate: enrollment.certificate,
        privateKey: enrollment.key.toBytes()
      },
      mspId: NETWORK_CONFIG.mspId,
      type: 'X.509'
    };

    await wallet.put('admin', identity);
    console.log('✅ Admin identity enrolled successfully');
    return identity;
  } catch (error) {
    console.error('❌ Failed to enroll admin:', error.message);
    throw error;
  }
};

export const registerUser = async (userId) => {
  try {
    const ca = await getCA();
    const wallet = await getWallet();

    const adminIdentity = await wallet.get('admin');
    if (!adminIdentity) {
      throw new Error('Admin identity not found. Run enrollAdmin first.');
    }

    const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
    const adminUser = await provider.getUserContext(adminIdentity, 'admin');

    const secret = await ca.register({
      enrollmentID: userId,
      affiliation: 'org1.department1',
      role: 'client'
    }, adminUser);

    const enrollment = await ca.enroll({
      enrollmentID: userId,
      enrollmentSecret: secret
    });

    const identity = {
      credentials: {
        certificate: enrollment.certificate,
        privateKey: enrollment.key.toBytes()
      },
      mspId: NETWORK_CONFIG.mspId,
      type: 'X.509'
    };

    await wallet.put(userId, identity);
    console.log(`✅ User ${userId} registered successfully`);
    return identity;
  } catch (error) {
    console.error(`❌ Failed to register user ${userId}:`, error.message);
    throw error;
  }
};

export default {
  connectionProfile,
  NETWORK_CONFIG,
  getWallet,
  getGateway,
  getContract,
  getCA,
  enrollAdmin,
  registerUser
};
