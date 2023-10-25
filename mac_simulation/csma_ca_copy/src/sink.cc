/* Sink
 *
 * Author: Leonardo Bonati
 * Created on Feb. 2018
 *
 */

#include <omnetpp.h>
#include <math.h>

#include "sink.h"

using namespace omnetpp;

#define SUB_CHANNELS true

namespace csma_ca {

void SinkNodeCSMACA::initialize()
{
    received_pkts = 0;
    collided = 0;

#if SUB_CHANNELS
    net = getIndex();
#else
    net = 0;
#endif

    EV << "Created sink " << getIndex() << " on net " << net << endl;
}

void SinkNodeCSMACA::handleMessage(cMessage *msg)
{
    cModule* c = getModuleByPath("SourceSink");

    // check if collision happened
    int cc_tx = (net == 0) ? (int) c->par("concurrent_tx_net0") : (int) c->par("concurrent_tx_net1");

    if (cc_tx > 1)
    {
        EV << "Collision" << endl;

        // increase collided packets counter
        collided++;
    }
    else    // successful transmission
    {
        EV << "Packet successfully received" << endl;

        // increase successful packets counter
        received_pkts++;
    }

    cancelAndDelete(msg);
}

void SinkNodeCSMACA::finish()
{
    cModule* c = getModuleByPath("SourceSink");

    double tot_p = received_pkts + collided + ((double) c->par("dropped_pkts").intValue());

    // print statistics
    EV << "Average delivery ratio: " << ((double) received_pkts) / tot_p * 100. << "%" << endl;
    EV << "Average latency: " << ((double) c->par("latency"))  / ((double) received_pkts) * 1000. << "ms" << endl;
    EV << "Average energy consumption: " << ((double) c->par("energy")) / ((double) received_pkts) * 1000. << "mJ" << endl;
}

}; // namespace


