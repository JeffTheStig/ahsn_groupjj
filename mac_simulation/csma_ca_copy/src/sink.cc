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
    sig_avg_delivery_ratio = registerSignal("sig_avg_delivery_ratio");
    sig_avg_latency = registerSignal("sig_avg_latency");
//    sig_latency = registerSignal("sig_latency");
    sig_avg_energy_cons = registerSignal("sig_avg_energy_cons");
//    sig_energy_cons = registerSignal("sig_energy_cons");
    sig_pkts_received = registerSignal("sig_pkts_received");
    sig_collided = registerSignal("sig_collided");
//    sig_pkts_timeout = registerSignal("sig_pkts_timeout");
    sig_pkts_dropped = registerSignal("sig_pkts_dropped");
//    sig_retries = registerSignal("sig_retries");
    sig_avg_retries = registerSignal("sig_avg_retries");
    sig_collided_net = registerSignal("sig_collided_net");
    sig_pkts_received_net = registerSignal("sig_pkts_received_net");

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
        c->par("collided_pkts") = ((int) c->par("collided_pkts") + 1);
        collided++;
        emit(sig_collided, (int) c->par("collided_pkts"));
        emit(sig_collided_net, collided);
        emit(sig_pkts_dropped, ((int) c->par("collided_pkts")) + ((int) c->par("dropped_pkts")));
    }
    else    // successful transmission
    {
        EV << "Packet successfully received" << endl;

        // increase successful packets counter
        received_pkts++;
        c->par("received_pkts") = ((int) c->par("received_pkts")) + 1;
        emit(sig_avg_latency, ((double) c->par("latency"))  / ((double) c->par("received_pkts").intValue()) * 1000.);
        emit(sig_avg_energy_cons, ((double) c->par("energy")) / ((double) c->par("received_pkts").intValue()) * 1000.);
        emit(sig_pkts_received, (int) c->par("received_pkts"));
        emit(sig_pkts_received_net, received_pkts);
    }
    double tot_p = ((double) c->par("received_pkts").intValue()) + ((double) c->par("collided_pkts").intValue()) + ((double) c->par("dropped_pkts").intValue());

    emit(sig_avg_delivery_ratio, ((double) c->par("received_pkts").intValue()) / tot_p * 100);
    emit(sig_avg_retries, ((double) c->par("total_retries").intValue()) / tot_p);
    cancelAndDelete(msg);
}

void SinkNodeCSMACA::finish()
{
    cModule* c = getModuleByPath("SourceSink");

    double tot_p = ((double) c->par("received_pkts").intValue()) + ((double) c->par("collided_pkts").intValue()) + ((double) c->par("dropped_pkts").intValue());

    // print statistics
    if (getIndex() == 0) {
        EV << "Average delivery ratio: " << ((double) c->par("received_pkts").intValue()) / tot_p * 100. << "%" << endl;
        EV << "Average latency: " << ((double) c->par("latency"))  / ((double) c->par("received_pkts").intValue()) * 1000. << "ms" << endl;
        EV << "Total latency: " << ((double) c->par("latency")) * 1000. << " ms" << endl;
        EV << "Average energy consumption: " << ((double) c->par("energy")) / ((double) c->par("received_pkts").intValue()) * 1000. << "mJ" << endl;
        EV << "Packages received: " << ((int) c->par("received_pkts"));
        EV << "Packages that where dropped due to collision: " << ((int) c->par("collided_pkts")) << endl;
        EV << "Packages that where dropped due to timeout: " << ((int) c->par("dropped_pkts")) << endl;
        EV << "Total packages dropped: " << ((int) c->par("collided_pkts")) + ((int) c->par("dropped_pkts")) << endl;
        EV << "Total retries: " << ((int) c->par("total_retries")) << endl;
        EV << "Average amount of retries: " << ((double) c->par("total_retries").intValue()) / tot_p << endl;
    }

    EV << "Packages that where dropped due to collision on sink " << getIndex() << ": " << collided << endl;
    EV << "Packages received on sink " << getIndex() << ": " << received_pkts;


}

}; // namespace


