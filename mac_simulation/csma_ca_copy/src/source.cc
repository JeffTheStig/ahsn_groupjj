/* Sensor node
 *
 * Author: Leonardo Bonati
 * Created on Feb. 2018
 *
 */

#include <omnetpp.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <algorithm>

#include "source.h"

using namespace omnetpp;

#define SUB_CHANNELS true

std::vector<int> overlapping_sources = {4, 0, 3, 5, 6};

namespace csma_ca {

SensorNodeCSMACA::SensorNodeCSMACA()
{
    // initialize pointers to nullptr
    backoff_timer_expired = nullptr;
    set_channel_busy[0] = nullptr;
    set_channel_free[0] = nullptr;
    set_channel_busy[1] = nullptr;
    set_channel_free[1] = nullptr;
    send_message = nullptr;
    decrease_concurrent_tx_counter[0] = nullptr;
    decrease_concurrent_tx_counter[1] = nullptr;
}

SensorNodeCSMACA::~SensorNodeCSMACA()
{
    // delete pointers
    if (backoff_timer_expired != nullptr) {
        cancelAndDelete (backoff_timer_expired);
    }

    if (set_channel_busy[0] != nullptr) {
        cancelAndDelete (set_channel_busy[0]);
    }

    if (set_channel_free[0] != nullptr) {
        cancelAndDelete (set_channel_free[0]);
    }

    if (set_channel_busy[1] != nullptr) {
            cancelAndDelete (set_channel_busy[1]);
    }

    if (set_channel_free[1] != nullptr) {
        cancelAndDelete (set_channel_free[1]);
    }

    if (send_message != nullptr) {
        cancelAndDelete (send_message);
    }

    if (decrease_concurrent_tx_counter[0] != nullptr) {
        cancelAndDelete (decrease_concurrent_tx_counter[0]);
    }

    if (decrease_concurrent_tx_counter[1] != nullptr) {
            cancelAndDelete (decrease_concurrent_tx_counter[1]);
        }
}

void SensorNodeCSMACA::initialize()
{
    // initialize algorithm parameters
    D_bp = par("D_bp_value");
    D_p = par("D_p_value");
    macMinBE = par("macMinBE_value");
    macMaxBE = par("macMaxBE_value");
    macMaxCSMABackoffs = par("macMaxCSMABackoffs_value");
    T = par("T_value");
    T_cca = par("T_cca_value");
    pkt_to_send = par("pkt_to_send_value");
    tot_pkt = pkt_to_send;

    pkt_creation_time = 0;

    p_tx = par("p_tx_value");
    p_rx = par("p_rx_value");

    // initialize algorithm variables
    nb = 0;
    be = macMinBE;

    if (pkt_to_send > 0)
    {
        pkt_creation_time = simTime().dbl();

        // wait for backoff time to expire and perform CCA
        if (backoff_timer_expired != nullptr) {
            cancelAndDelete (backoff_timer_expired);
        }

        backoff_timer_expired = new cMessage("backoff_timer_expired");
        scheduleAt(simTime() + generate_backoff_time(), backoff_timer_expired);
    }

#if SUB_CHANNELS
    cModule* c = getModuleByPath("SourceSink");
    net = (getIndex() >= (int) c->par("n")) ? 1 : 0;
    net = (std::count(overlapping_sources.begin(), overlapping_sources.end(), getIndex())) ? -1 : net;
# else
    net = 0;
#endif

    EV << "Created source with id " << getIndex() << " on net " << net << endl;
}

void SensorNodeCSMACA::handleMessage(cMessage *msg)
{
    if (msg==backoff_timer_expired)
    {
        EV << "Backoff timer expired" << endl;

        // check if channel is free
        if (perform_cca()){
            EV << "Channel is free" << endl;

            // change channel state to busy
            if (net != -1) {
                setChannelBusy(net);
            } else {
                setChannelBusy(0);
                setChannelBusy(1);
            }

        }
        else  // channel is busy
        {
            EV << "Channel is busy" << endl;

            // update variables
            nb++;
            be++;
            if (be > macMaxBE)
            {
                be = macMaxBE;
            }

            if (nb <= macMaxCSMABackoffs){

                EV << "Retry" << endl;

                // retry
                if (backoff_timer_expired != nullptr) {
                    cancelAndDelete (backoff_timer_expired);
                }

                backoff_timer_expired = new cMessage("backoff_timer_expired");
                scheduleAt(simTime() + D_bp + generate_backoff_time(), backoff_timer_expired);
            }
            else
            {
                EV << "Drop packet" << endl;

                // drop packet
                cModule* c = getModuleByPath("SourceSink");
                c->par("dropped_pkts") = ((int) c->par("dropped_pkts")) + 1;

                // decrease counter and repeat process if there are still packets to send
                decrease_and_repeat();
            }
        }
    }
    else if (msg==set_channel_busy[0])
    {
        if (net == 0 || net == -1) {
            EV << "Set channel 0 busy" << endl;

            // set channel state to busy
            set_channel_state(false, 0);

            // send actual message - add 1 microsecond to compensate and start
            //  at the beginning of the slot
            if (send_message != nullptr) {
                cancelAndDelete (send_message);
            }

            send_message = new cMessage("send_message");
            scheduleAt(simTime() + 0.000001, send_message);
        }
    }
    else if (msg==set_channel_busy[1])
        {
            if (net == 1 || net == -1) {
                EV << "Set channel 1 busy" << endl;

                // set channel state to busy
                set_channel_state(false, 1);

                // send actual message - add 1 microsecond to compensate and start
                //  at the beginning of the slot
                if (send_message != nullptr) {
                    cancelAndDelete (send_message);
                }

                send_message = new cMessage("send_message");
                scheduleAt(simTime() + 0.000001, send_message);
            }
        }
    else if (msg==set_channel_free[0])
    {
        if (net == 0 || net == -1) {
            EV << "Set channel 0 free" << endl;

            // set channel state to free
            set_channel_state(true, 0);

            cModule* c = getModuleByPath("SourceSink");

            if (((int) c->par("concurrent_tx_net0")) <= 1)
            {
                // compute packet latency
                double tmp_lat = 0;
                tmp_lat = simTime().dbl() - pkt_creation_time;
                cModule* c = getModuleByPath("SourceSink");
                c->par("latency") = ((double) c->par("latency")) + tmp_lat;
            }

            // decrease counter of transmissions in progress
            if (decrease_concurrent_tx_counter[0] != nullptr) {
                cancelAndDelete (decrease_concurrent_tx_counter[0]);
            }

            decrease_concurrent_tx_counter[0] = new cMessage("decrease_concurrent_tx_counter_0");
            scheduleAt(simTime() + 0.000001, decrease_concurrent_tx_counter[0]);
        }
    }
    else if (msg==set_channel_free[1])
        {
            if (net == 1 || net == -1) {
                EV << "Set channel 1 free" << endl;

                // set channel state to free
                set_channel_state(true, 1);

                cModule* c = getModuleByPath("SourceSink");

                if (((int) c->par("concurrent_tx_net1")) <= 1)
                {
                    // compute packet latency
                    double tmp_lat = 0;
                    tmp_lat = simTime().dbl() - pkt_creation_time;
                    cModule* c = getModuleByPath("SourceSink");
                    c->par("latency") = ((double) c->par("latency")) + tmp_lat;
                }

                // decrease counter of transmissions in progress
                if (decrease_concurrent_tx_counter[1] != nullptr) {
                    cancelAndDelete (decrease_concurrent_tx_counter[1]);
                }

                decrease_concurrent_tx_counter[1] = new cMessage("decrease_concurrent_tx_counter_1");
                scheduleAt(simTime() + 0.000001, decrease_concurrent_tx_counter[1]);
            }
        }

    else if (msg==send_message)
    {
        cModule* c = getModuleByPath("SourceSink");

        int k = 0;
        if (net == -1) {
            int n = gateSize("out");
            int k = intuniform(0, n-1);
        }

        EV << "Send message on channel " << net << endl;

        // update energy consumption
        c->par("energy") = ((double) c->par("energy")) + p_tx * ((double) D_p);

        // increase counters
        if (net == 0) {
            c->par("concurrent_tx_net0") = ((int) c->par("concurrent_tx_net0")) + 1;
        } else if (net == 1) {
            c->par("concurrent_tx_net1") = ((int) c->par("concurrent_tx_net1")) + 1;
        }else {
            c->par("concurrent_tx_net0") = ((int) c->par("concurrent_tx_net0")) + 1;
            c->par("concurrent_tx_net1") = ((int) c->par("concurrent_tx_net1")) + 1;
        }

        c->par("tx_pkts") = ((int) c->par("tx_pkts")) + 1;

        // send actual packet to the sink
        cMessage *data_pkt = new cMessage("data_pkt");
        send(data_pkt, "out", k);

        // set channel state to free
        if (net != -1) {
            SensorNodeCSMACA::setChannelFree(net);
        } else {
            SensorNodeCSMACA::setChannelFree(0);
            SensorNodeCSMACA::setChannelFree(1);
        }

    }
    else if (msg==decrease_concurrent_tx_counter[0])
    {
        cModule* c = getModuleByPath("SourceSink");
        c->par("concurrent_tx_net0") = ((int) c->par("concurrent_tx_net0")) - 1;

        // decrease counter and repeat process if there are still packets to send
        if(net != -1) {
            decrease_and_repeat(); // Prevent this channel running twice for node on both nets.
        }
    }
    else if (msg==decrease_concurrent_tx_counter[1])
    {
        cModule* c = getModuleByPath("SourceSink");
        c->par("concurrent_tx_net1") = ((int) c->par("concurrent_tx_net1")) - 1;

        // decrease counter and repeat process if there are still packets to send
        decrease_and_repeat();
    }

}

// returns true if channel free, else false
bool SensorNodeCSMACA::perform_cca()
{
    EV << "Perform CCA" << endl;

    cModule* c = getModuleByPath("SourceSink");

    // update energy consumption
    c->par("energy") = ((double) c->par("energy")) + p_rx * ((double) T_cca);

    bool result = false;

    if (net == 0) {
        result = (bool) c->par("channel_free_net0");
    } else if (net == 1) {
        result = (bool) c->par("channel_free_net1");
    } else {
        result = (bool) c->par("channel_free_net0") && (bool) c->par("channel_free_net1") ;
    }


    return result;
}

// set channel_free: true=free, false=busy
void SensorNodeCSMACA::set_channel_state(bool state, int chan)
{
    cModule* c = getModuleByPath("SourceSink");
    if (chan == 0) {
        c->par("channel_free_net0") = state;
    } else {
        c->par("channel_free_net1") = state;
    }

}

// obtain new backoff time
double SensorNodeCSMACA::generate_backoff_time(){

    int rv_int = intuniform(0, pow(2, be));
    double tmp = ((double) rv_int) * D_bp;

    return tmp;
}

// decrease packet counter and repeat process if there are still packets to send
void SensorNodeCSMACA::decrease_and_repeat()
{
    // reset variables
     nb = 0;
     be = macMinBE;

     // decrease counter
     pkt_to_send--;

    // repeat process
    if (pkt_to_send > 0){

        if (backoff_timer_expired != nullptr) {
            cancelAndDelete (backoff_timer_expired);
        }

        // schedule at next "T" instant
        backoff_timer_expired = new cMessage("backoff_timer_expired");
        scheduleAt((tot_pkt - pkt_to_send) * T + generate_backoff_time(), backoff_timer_expired);

        pkt_creation_time = (tot_pkt - pkt_to_send) * T;
    }
}

void SensorNodeCSMACA::finish()
{

}

void SensorNodeCSMACA::setChannelBusy(int chan) {
    if (set_channel_busy[chan] != nullptr) {
        cancelAndDelete (set_channel_busy[chan]);
    }

    if (chan == 0) {
        set_channel_busy[0] = new cMessage("set_channel_busy_net0");
    } else {
        set_channel_busy[1] = new cMessage("set_channel_busy_net1");
    }
    scheduleAt(simTime() + D_bp - 0.000001, set_channel_busy[chan]);
}

void SensorNodeCSMACA::setChannelFree(int chan) {
    // set channel state to free
    if (set_channel_free[chan] != nullptr) {
        cancelAndDelete (set_channel_free[chan]);
    }

    if (chan == 0) {
        set_channel_free[0] = new cMessage("set_channel_free_net0");
    } else {
        set_channel_free[1] = new cMessage("set_channel_free_net1");
    }
    scheduleAt(simTime() + D_p, set_channel_free[chan]);
}

}; // namespace
