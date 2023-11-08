//
// Generated file, do not edit! Created by opp_msgtool 6.0 from inet/linklayer/tun/TunControlInfo.msg.
//

#ifndef __INET_TUNCONTROLINFO_M_H
#define __INET_TUNCONTROLINFO_M_H

#if defined(__clang__)
#  pragma clang diagnostic ignored "-Wreserved-id-macro"
#endif
#include <omnetpp.h>

// opp_msgtool version check
#define MSGC_VERSION 0x0600
#if (MSGC_VERSION!=OMNETPP_VERSION)
#    error Version mismatch! Probably this file was generated by an earlier version of opp_msgtool: 'make clean' should help.
#endif

// dll export symbol
#ifndef INET_API
#  if defined(INET_EXPORT)
#    define INET_API  OPP_DLLEXPORT
#  elif defined(INET_IMPORT)
#    define INET_API  OPP_DLLIMPORT
#  else
#    define INET_API
#  endif
#endif


namespace inet {

class TunControlInfo;
class TunOpenCommand;
class TunCloseCommand;
class TunDestroyCommand;
class TunSocketClosedIndication;

}  // namespace inet

#include "inet/common/INETDefs_m.h" // import inet.common.INETDefs


namespace inet {

/**
 * Enum generated from <tt>inet/linklayer/tun/TunControlInfo.msg:13</tt> by opp_msgtool.
 * <pre>
 * enum TunCommandCode
 * {
 *     TUN_C_OPEN = 1;
 *     TUN_C_CLOSE = 2;
 *     TUN_C_DESTROY = 3;
 *     TUN_C_DATA = 4;
 * }
 * </pre>
 */
enum TunCommandCode {
    TUN_C_OPEN = 1,
    TUN_C_CLOSE = 2,
    TUN_C_DESTROY = 3,
    TUN_C_DATA = 4
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunCommandCode& e) { b->pack(static_cast<int>(e)); }
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunCommandCode& e) { int n; b->unpack(n); e = static_cast<TunCommandCode>(n); }

/**
 * Enum generated from <tt>inet/linklayer/tun/TunControlInfo.msg:21</tt> by opp_msgtool.
 * <pre>
 * enum TunSocketIndication
 * {
 *     TUN_I_CLOSED = 2;
 *     TUN_I_DATA = 4;
 * }
 * </pre>
 */
enum TunSocketIndication {
    TUN_I_CLOSED = 2,
    TUN_I_DATA = 4
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunSocketIndication& e) { b->pack(static_cast<int>(e)); }
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunSocketIndication& e) { int n; b->unpack(n); e = static_cast<TunSocketIndication>(n); }

/**
 * Class generated from <tt>inet/linklayer/tun/TunControlInfo.msg:27</tt> by opp_msgtool.
 * <pre>
 * class TunControlInfo extends cObject
 * {
 * }
 * </pre>
 */
class INET_API TunControlInfo : public ::omnetpp::cObject
{
  protected:

  private:
    void copy(const TunControlInfo& other);

  protected:
    bool operator==(const TunControlInfo&) = delete;

  public:
    TunControlInfo();
    TunControlInfo(const TunControlInfo& other);
    virtual ~TunControlInfo();
    TunControlInfo& operator=(const TunControlInfo& other);
    virtual TunControlInfo *dup() const override {return new TunControlInfo(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunControlInfo& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunControlInfo& obj) {obj.parsimUnpack(b);}

/**
 * Class generated from <tt>inet/linklayer/tun/TunControlInfo.msg:31</tt> by opp_msgtool.
 * <pre>
 * class TunOpenCommand extends TunControlInfo
 * {
 * }
 * </pre>
 */
class INET_API TunOpenCommand : public ::inet::TunControlInfo
{
  protected:

  private:
    void copy(const TunOpenCommand& other);

  protected:
    bool operator==(const TunOpenCommand&) = delete;

  public:
    TunOpenCommand();
    TunOpenCommand(const TunOpenCommand& other);
    virtual ~TunOpenCommand();
    TunOpenCommand& operator=(const TunOpenCommand& other);
    virtual TunOpenCommand *dup() const override {return new TunOpenCommand(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunOpenCommand& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunOpenCommand& obj) {obj.parsimUnpack(b);}

/**
 * Class generated from <tt>inet/linklayer/tun/TunControlInfo.msg:35</tt> by opp_msgtool.
 * <pre>
 * class TunCloseCommand extends TunControlInfo
 * {
 * }
 * </pre>
 */
class INET_API TunCloseCommand : public ::inet::TunControlInfo
{
  protected:

  private:
    void copy(const TunCloseCommand& other);

  protected:
    bool operator==(const TunCloseCommand&) = delete;

  public:
    TunCloseCommand();
    TunCloseCommand(const TunCloseCommand& other);
    virtual ~TunCloseCommand();
    TunCloseCommand& operator=(const TunCloseCommand& other);
    virtual TunCloseCommand *dup() const override {return new TunCloseCommand(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunCloseCommand& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunCloseCommand& obj) {obj.parsimUnpack(b);}

/**
 * Class generated from <tt>inet/linklayer/tun/TunControlInfo.msg:39</tt> by opp_msgtool.
 * <pre>
 * class TunDestroyCommand extends TunControlInfo
 * {
 * }
 * </pre>
 */
class INET_API TunDestroyCommand : public ::inet::TunControlInfo
{
  protected:

  private:
    void copy(const TunDestroyCommand& other);

  protected:
    bool operator==(const TunDestroyCommand&) = delete;

  public:
    TunDestroyCommand();
    TunDestroyCommand(const TunDestroyCommand& other);
    virtual ~TunDestroyCommand();
    TunDestroyCommand& operator=(const TunDestroyCommand& other);
    virtual TunDestroyCommand *dup() const override {return new TunDestroyCommand(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunDestroyCommand& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunDestroyCommand& obj) {obj.parsimUnpack(b);}

/**
 * Class generated from <tt>inet/linklayer/tun/TunControlInfo.msg:43</tt> by opp_msgtool.
 * <pre>
 * class TunSocketClosedIndication extends TunControlInfo
 * {
 * }
 * </pre>
 */
class INET_API TunSocketClosedIndication : public ::inet::TunControlInfo
{
  protected:

  private:
    void copy(const TunSocketClosedIndication& other);

  protected:
    bool operator==(const TunSocketClosedIndication&) = delete;

  public:
    TunSocketClosedIndication();
    TunSocketClosedIndication(const TunSocketClosedIndication& other);
    virtual ~TunSocketClosedIndication();
    TunSocketClosedIndication& operator=(const TunSocketClosedIndication& other);
    virtual TunSocketClosedIndication *dup() const override {return new TunSocketClosedIndication(*this);}
    virtual void parsimPack(omnetpp::cCommBuffer *b) const override;
    virtual void parsimUnpack(omnetpp::cCommBuffer *b) override;
};

inline void doParsimPacking(omnetpp::cCommBuffer *b, const TunSocketClosedIndication& obj) {obj.parsimPack(b);}
inline void doParsimUnpacking(omnetpp::cCommBuffer *b, TunSocketClosedIndication& obj) {obj.parsimUnpack(b);}


}  // namespace inet


namespace omnetpp {

template<> inline inet::TunControlInfo *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::TunControlInfo*>(ptr.get<cObject>()); }
template<> inline inet::TunOpenCommand *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::TunOpenCommand*>(ptr.get<cObject>()); }
template<> inline inet::TunCloseCommand *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::TunCloseCommand*>(ptr.get<cObject>()); }
template<> inline inet::TunDestroyCommand *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::TunDestroyCommand*>(ptr.get<cObject>()); }
template<> inline inet::TunSocketClosedIndication *fromAnyPtr(any_ptr ptr) { return check_and_cast<inet::TunSocketClosedIndication*>(ptr.get<cObject>()); }

}  // namespace omnetpp

#endif // ifndef __INET_TUNCONTROLINFO_M_H
